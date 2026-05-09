"""
Singapore Schools Scraper

Scrapes school information from the MOE SchoolFinder portal.
https://www.moe.gov.sg/schoolfinder

MOE SchoolFinder is a Next.js App Router application. All school records for a
given school type are pre-loaded into the page as a JSON payload embedded inside
a `self.__next_f.push([1, "...escaped JSON..."])` script tag — no per-school
clicking is required. The scraper simply:

  1. Navigates to each school-type URL with Selenium (triggers SSR)
  2. Grabs driver.page_source
  3. Locates the script tag containing `school_name`
  4. Unescapes and parses the Next.js JSON payload
  5. Recursively finds the list of school objects inside the nested structure
  6. Maps each raw record to a flat schema

Supported school types (pass via `school_types` kwarg to scrape()):
  - 'preschool'  →  MOE Kindergartens
  - 'primary'    →  Primary schools       (extend later)
  - 'secondary'  →  Secondary schools     (extend later)
  - 'jc'         →  Junior colleges       (extend later)
"""

import json
import re
import time
import logging
import pandas as pd
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SchoolsScraper(BaseScraper):
    """Scraper for Singapore school data from MOE SchoolFinder"""

    # Map caller-facing school type labels to their MOE SchoolFinder URLs.
    SCHOOL_TYPE_URLS = {
        "preschool": "https://www.moe.gov.sg/schoolfinder/moe%20kindergarten",
        "primary":   "https://www.moe.gov.sg/schoolfinder/primary%20school",
        "secondary": "https://www.moe.gov.sg/schoolfinder/secondary%20school",
        "jc":        "https://www.moe.gov.sg/schoolfinder/post%20secondary-jc%20school",
        # 'college' accepted as an alias for 'jc' (matches main.py usage)
        "college":   "https://www.moe.gov.sg/schoolfinder/post%20secondary-jc%20school",
    }

    def __init__(self, headless=True, implicit_wait=10):
        """Initialise the schools scraper."""
        super().__init__(headless=headless, implicit_wait=implicit_wait)
        self.schools = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape(self, url, school_types=None):
        """
        Scrape MOE SchoolFinder for one or more school types.

        Args:
            url (str): Base SchoolFinder URL (used as a fallback; each type
                       has its own URL defined in SCHOOL_TYPE_URLS).
            school_types (list[str] | None): Types to scrape. Defaults to
                         ['preschool']. Supported values: 'preschool',
                         'primary', 'secondary', 'jc', 'college'.

        Returns:
            pd.DataFrame: One row per school with columns:
                name, type, address, postal_code, phone, email,
                website, zone, school_active, is_enrolling,
                latitude, longitude
        """
        if school_types is None:
            school_types = ["preschool"]

        self.setup_driver()
        try:
            for school_type in school_types:
                type_url = self.SCHOOL_TYPE_URLS.get(school_type)
                if type_url is None:
                    logger.warning(
                        f"Unknown school type '{school_type}' — skipping. "
                        f"Valid types: {list(self.SCHOOL_TYPE_URLS.keys())}"
                    )
                    continue
                self._scrape_school_type(type_url, school_type)

            logger.info(f"Total schools extracted: {len(self.schools)}")
            return self.to_dataframe()
        finally:
            self.close_driver()

    def to_dataframe(self):
        """Convert scraped schools list to a DataFrame."""
        df = pd.DataFrame(self.schools)
        logger.info(f"Converted {len(df)} schools to DataFrame")
        return df

    # ------------------------------------------------------------------
    # Per-type scraping
    # ------------------------------------------------------------------

    def _scrape_school_type(self, url, school_type):
        """
        Navigate to a school-type page and extract all school records.

        Args:
            url (str): MOE SchoolFinder URL for this school type.
            school_type (str): Label used in the output ('preschool', etc.).
        """
        logger.info(f"Scraping '{school_type}' schools from {url}")
        self.get_page(url)

        # Give Next.js a moment to finish streaming the RSC payload into
        # the page's script tags before we grab the source.
        time.sleep(3)

        page_source = self.driver.page_source
        schools = self._extract_schools_from_page(page_source, school_type)
        logger.info(f"Extracted {len(schools)} '{school_type}' schools")
        self.schools.extend(schools)

    # ------------------------------------------------------------------
    # HTML / JSON extraction
    # ------------------------------------------------------------------

    def _extract_schools_from_page(self, page_source, school_type):
        """
        Find and parse the Next.js script tag that holds school data.

        Args:
            page_source (str): Full HTML source of the page.
            school_type (str): School type label for logging / output.

        Returns:
            list[dict]: List of flat school record dicts.
        """
        soup = BeautifulSoup(page_source, "html.parser")

        # Locate the first <script> whose text contains 'school_name'.
        # In Next.js App Router this is always a self.__next_f.push() call.
        target_script = None
        for script in soup.find_all("script"):
            content = script.string
            if content and "school_name" in content:
                target_script = content
                break

        if not target_script:
            logger.warning(
                f"No school-data script tag found for '{school_type}'. "
                "The page structure may have changed."
            )
            return []

        return self._parse_schools_from_script(target_script, school_type)

    def _parse_schools_from_script(self, script_content, school_type):
        """
        Extract school objects from a Next.js `self.__next_f.push()` script.

        MOE SchoolFinder uses the Next.js App Router RSC Wire Protocol:

            self.__next_f.push([1, "...double-escaped RSC payload..."])

        The inner string is JS-escaped, so decoding happens in two stages:

            Stage 1  json.loads('"' + captured + '"')
                     → raw RSC text  (newline-delimited chunks)

        Each RSC chunk has the form:
            {id}:{json_value}\n
        e.g.
            33:["$","$L35",null,{"schools":[...], ...}]\n

        The school list lives at chunk_value[3]["schools"].

        Args:
            script_content (str): Raw text of the <script> tag.
            school_type (str): School type label.

        Returns:
            list[dict]: Parsed school records.
        """
        # --- Attempt 1: RSC Wire Protocol parsing ------------------------
        push_pattern = re.compile(
            r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)',
            re.DOTALL,
        )

        for push_match in push_pattern.finditer(script_content):
            candidate = push_match.group(1)
            if "school_name" not in candidate:
                continue

            try:
                # Stage 1: unescape the JS string → raw RSC text
                rsc_text = json.loads(f'"{candidate}"')
            except (json.JSONDecodeError, ValueError) as exc:
                logger.debug(f"JS unescape failed: {exc}")
                continue

            # Stage 2: find the RSC chunk line that contains school_name,
            # strip its "{id}:" prefix, then parse the JSON value.
            for rsc_line in rsc_text.splitlines():
                if "school_name" not in rsc_line:
                    continue

                colon_idx = rsc_line.index(":")
                json_value = rsc_line[colon_idx + 1:]

                try:
                    chunk_data = json.loads(json_value)
                except (json.JSONDecodeError, ValueError) as exc:
                    logger.debug(f"RSC chunk JSON parse failed: {exc}")
                    continue

                # Known structure: ["$", "$L35", null, {schools: [...], ...}]
                # Try the direct path first (fast), then fall back to recursion.
                raw_schools = self._extract_schools_direct(chunk_data)
                if raw_schools is None:
                    raw_schools = self._find_schools_in_data(chunk_data)

                if raw_schools:
                    logger.info(
                        f"Found {len(raw_schools)} raw school records "
                        f"(RSC payload) for '{school_type}'"
                    )
                    return [
                        self._parse_school_record(r, school_type)
                        for r in raw_schools
                        if r.get("school_name")
                    ]

        # --- Attempt 2: fallback regex extraction ------------------------
        logger.warning(
            f"RSC parsing did not match for '{school_type}'. "
            "Falling back to regex extraction — data may be incomplete."
        )
        return self._fallback_parse(script_content, school_type)

    # ------------------------------------------------------------------
    # Data-structure traversal
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_schools_direct(chunk_data):
        """
        Try the known RSC chunk structure directly (fast path).

        MOE SchoolFinder chunks arrive as:
            ["$", "$L35", null, {"schools": [...], "areas": [...], ...}]

        If this shape holds, return chunk_data[3]["schools"] directly.
        Returns None if the shape doesn't match — caller falls back to
        _find_schools_in_data.

        Args:
            chunk_data: Parsed Python value from an RSC chunk.

        Returns:
            list[dict] | None
        """
        try:
            if (
                isinstance(chunk_data, list)
                and len(chunk_data) >= 4
                and isinstance(chunk_data[3], dict)
                and "schools" in chunk_data[3]
            ):
                schools = chunk_data[3]["schools"]
                if isinstance(schools, list) and schools:
                    return schools
        except Exception:
            pass
        return None

    def _find_schools_in_data(self, data):
        """
        Recursively search a nested Python structure for the list of school
        objects (i.e. dicts that contain the key 'school_name').

        Args:
            data: Any Python value (dict, list, str, …).

        Returns:
            list[dict] | None: The school list, or None if not found.
        """
        if isinstance(data, list):
            # Is this list a collection of school objects?
            school_items = [
                item for item in data
                if isinstance(item, dict) and "school_name" in item
            ]
            if school_items:
                return school_items

            # Otherwise recurse into each element.
            for item in data:
                result = self._find_schools_in_data(item)
                if result:
                    return result

        elif isinstance(data, dict):
            # Is this dict itself a single school record?
            if "school_name" in data:
                return [data]

            # Recurse into each value.
            for value in data.values():
                result = self._find_schools_in_data(value)
                if result:
                    return result

        return None

    # ------------------------------------------------------------------
    # Field mapping
    # ------------------------------------------------------------------

    def _parse_school_record(self, raw, school_type):
        """
        Map a raw MOE SchoolFinder school dict to our flat output schema.

        Args:
            raw (dict): Raw school object from the JSON payload.
            school_type (str): Caller-supplied school type label.

        Returns:
            dict: Flat record with standardised field names.
        """
        # school_area is a nested object: {"id": 4, "name": "Bukit Merah", ...}
        area = raw.get("school_area") or {}
        zone = area.get("name", "") if isinstance(area, dict) else ""

        # education_tags is a list, e.g. ["MOE Kindergarten"]
        tags = raw.get("education_tags") or []
        education_tag = tags[0] if tags else school_type

        # phone: MOE uses two different field names across school types
        phone = (
            raw.get("school_telephone_number")
            or raw.get("school_telephone_no")
            or ""
        )

        # email: similarly two possible field names
        email = (
            raw.get("school_email")
            or raw.get("school_email_address")
            or ""
        )

        return {
            "name":          raw.get("school_name", ""),
            "type":          school_type,
            "education_tag": education_tag,
            "address":       raw.get("school_address", ""),
            "postal_code":   str(raw.get("school_address_postal_code", "")),
            "phone":         phone,
            "email":         email,
            "website":       raw.get("school_website_url", ""),
            "zone":          zone,
            "school_active": raw.get("school_active", True),
            "is_enrolling":  raw.get("is_enrolling", True),
            # lat/lng are currently null in the MOE data; geocode later
            # using postal_code via the OneMap Singapore API.
            "latitude":      raw.get("latitude"),
            "longitude":     raw.get("longitude"),
        }

    # ------------------------------------------------------------------
    # Fallback parser
    # ------------------------------------------------------------------

    def _fallback_parse(self, script_content, school_type):
        """
        Best-effort extraction when the standard Next.js wrapper pattern
        doesn't match (e.g. if MOE changes their frontend framework version).

        Scans for `"school_name":"..."` patterns and attempts to build
        minimal records from surrounding field matches.

        Args:
            script_content (str): Raw script tag text.
            school_type (str): School type label.

        Returns:
            list[dict]: Partial school records (name-only on worst case).
        """
        schools = []

        # Greedy attempt: try to pull out self-contained JSON objects that
        # contain school_name by finding balanced braces.
        for name_match in re.finditer(
            r'"school_name"\s*:\s*"([^"]+)"', script_content
        ):
            school_name = name_match.group(1)
            if not school_name:
                continue

            # Try to find sibling fields in a ~2000-char window around the match.
            start = max(0, name_match.start() - 500)
            end   = min(len(script_content), name_match.end() + 1500)
            window = script_content[start:end]

            def _grab(field):
                m = re.search(rf'"{field}"\s*:\s*"([^"]*)"', window)
                return m.group(1) if m else ""

            def _grab_bool(field, default=True):
                m = re.search(rf'"{field}"\s*:\s*(true|false)', window)
                if m:
                    return m.group(1) == "true"
                return default

            area_m = re.search(
                r'"school_area"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', window
            )
            zone = area_m.group(1) if area_m else ""

            schools.append({
                "name":          school_name,
                "type":          school_type,
                "education_tag": school_type,
                "address":       _grab("school_address"),
                "postal_code":   _grab("school_address_postal_code"),
                "phone":         _grab("school_telephone_number") or _grab("school_telephone_no"),
                "email":         _grab("school_email") or _grab("school_email_address"),
                "website":       _grab("school_website_url"),
                "zone":          zone,
                "school_active": _grab_bool("school_active"),
                "is_enrolling":  _grab_bool("is_enrolling"),
                "latitude":      None,
                "longitude":     None,
            })

        logger.info(
            f"Fallback parser extracted {len(schools)} '{school_type}' records"
        )
        return schools


# ---------------------------------------------------------------------------
# Standalone usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = SchoolsScraper(headless=True)
    df = scraper.scrape(
        url="https://www.moe.gov.sg/schoolfinder",
        school_types=["preschool"],
    )

    print(f"\nScraped {len(df)} schools")
    print("\nFirst few schools:")
    print(df.head(10))
    print("\nColumns:", list(df.columns))

    scraper.save_to_csv("data/raw/schools.csv")
