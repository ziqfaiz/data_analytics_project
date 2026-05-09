"""
URA PMI Residential Transaction Scraper  — v5 (download endpoint)

How it works
─────────────
  • POSTs directly to the CSV download endpoint (NOT the search page):
      /property-market-information/pmiSearchResidentialTransactionDownload
  • Each POST returns a CSV file with ALL results for that query — no
    pagination, no HTML table parsing needed.
  • Session cookies + CSRF token are acquired via a single GET to the
    main search page before any downloads start.

Loop strategy
─────────────
  28 postal districts  ×  4 property types  =  112 downloads
  Each download returns a complete CSV for that slice, well under the
  server's 100 000-row cap per query.

locationDetails format  (confirmed from live network capture)
─────────────────────────────────────────────────────────────
  ["postalDistrict", "D01 / Raffles Place, Cecil, Marina, People's Park"]
  — a flat 2-element JSON array: the key "postalDistrict" and the full
  district label as shown in the URA dropdown.
"""

import json
import logging
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── URLs ───────────────────────────────────────────────────────────────────────

PMI_BASE         = "https://eservice.ura.gov.sg"
PMI_SEARCH_URL   = f"{PMI_BASE}/property-market-information/pmiResidentialTransactionSearch"
PMI_DOWNLOAD_URL = f"{PMI_BASE}/property-market-information/pmiSearchResidentialTransactionDownload"
PMI_POPUP_URL    = f"{PMI_BASE}/property-market-information/pmiSearchResidentialTransactionLocationPopup"

# ── Postal district labels (confirmed D01 from live cURL; rest from URA docs) ─

POSTAL_DISTRICTS = [
    "D01 / Raffles Place, Cecil, Marina, People's Park",
    "D02 / Anson, Tanjong Pagar",
    "D03 / Queenstown, Tiong Bahru",
    "D04 / Telok Blangah, Harbourfront",
    "D05 / Pasir Panjang, Hong Leong Garden, Clementi New Town",
    "D06 / High Street, Beach Road (part)",
    "D07 / Middle Road, Golden Mile",
    "D08 / Little India",
    "D09 / Orchard, Cairnhill, River Valley",
    "D10 / Ardmore, Bukit Timah, Holland Road, Tanglin",
    "D11 / Watten Estate, Novena, Thomson",
    "D12 / Balestier, Toa Payoh, Serangoon",
    "D13 / Macpherson, Braddell",
    "D14 / Geylang, Eunos",
    "D15 / Katong, Joo Chiat, Amber Road",
    "D16 / Bedok, Upper East Coast, Eastwood, Kew Drive",
    "D17 / Loyang, Changi",
    "D18 / Tampines, Pasir Ris",
    "D19 / Serangoon Garden, Hougang, Ponggol",
    "D20 / Bishan, Ang Mo Kio",
    "D21 / Upper Bukit Timah, Clementi Park, Ulu Pandan",
    "D22 / Jurong",
    "D23 / Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang",
    "D24 / Lim Chu Kang, Tengah",
    "D25 / Kranji, Woodgrove",
    "D26 / Upper Thomson, Springleaf",
    "D27 / Yishun, Sembawang",
    "D28 / Seletar",
]

PROPERTY_TYPE_OPTIONS = {
    "1": "Landed Properties (Non-Strata)",
    "2": "Strata Landed",
    "3": "Apartments & Condominiums",
    "4": "Executive Condominiums",
}

ALL_DISTRICTS  = list(range(1, 29))
RESULT_COLUMNS = [
    "project_name", "transacted_price", "area_sqft", "unit_price_psf",
    "sale_date", "street_name", "type_of_sale", "type_of_area",
    "area_sqm", "unit_price_psm", "nett_price", "property_type",
    "num_units", "tenure", "postal_district", "market_segment", "floor_level",
]

# ── Scraper ────────────────────────────────────────────────────────────────────

class URARealestateScraper:
    """
    Downloads residential transaction CSVs from URA PMI.

    Usage
    ─────
    scraper = URARealestateScraper()
    df = scraper.scrape(districts=[0, 1])          # first 2 districts (test)
    df = scraper.scrape()                           # all 28 × 4
    scraper.save_to_csv("data/raw/ura_pmi_transactions.csv")
    """

    def __init__(self, headless=True, implicit_wait=15):
        # headless / implicit_wait kept for API compatibility with existing code
        self.property_data = []
        self.transactions  = self.property_data
        self._session      = None
        self._csrf         = None

    # ── Public API ─────────────────────────────────────────────────────────────

    def scrape(self, url=None, districts=None, property_type_ids=None,
               postal_districts=None, **kwargs):
        """
        Download and combine CSVs for every district × property-type combo.

        Args
        ────
        districts         : List of 0-based indices into POSTAL_DISTRICTS
                            (default: all 28). Use [0, 1] for a quick test.
        property_type_ids : List of str "1"–"4" (default: all 4).
        postal_districts  : Ignored — kept for backwards compatibility.
        """
        self.property_data.clear()

        # Resolve which district labels to use
        if districts is not None:
            labels = [POSTAL_DISTRICTS[i] for i in districts]
        else:
            labels = POSTAL_DISTRICTS

        # Optionally verify labels against the live popup
        live_labels = self._fetch_district_labels()
        if live_labels:
            logger.info(f"Live popup returned {len(live_labels)} district labels")
            # Use live labels if they differ (catches any naming changes)
            if set(live_labels) != set(labels) and districts is None:
                logger.info("Using live labels from popup")
                labels = live_labels
        else:
            logger.info("Using hardcoded district labels")

        ptypes = property_type_ids or list(PROPERTY_TYPE_OPTIONS.keys())
        total  = len(labels) * len(ptypes)
        n      = 0

        self._init_session()

        for label in labels:
            for ptype_id in ptypes:
                n += 1
                ptype_name = PROPERTY_TYPE_OPTIONS.get(str(ptype_id), ptype_id)
                logger.info(f"[{n}/{total}]  {label}  /  {ptype_name}")

                try:
                    df = self._download_csv(label, str(ptype_id))
                    if df is not None and not df.empty:
                        self.property_data.extend(df.to_dict("records"))
                        logger.info(f"  → {len(df)} rows  (total: {len(self.property_data)})")
                    else:
                        logger.info("  → 0 rows (no transactions)")
                except Exception as exc:
                    logger.error(f"  Failed: {exc}")

                time.sleep(0.5)   # polite delay

        logger.info(f"Done — {len(self.property_data)} total records")
        return self.to_dataframe()

    def to_dataframe(self):
        if not self.property_data:
            return pd.DataFrame(columns=RESULT_COLUMNS)
        return pd.DataFrame(self.property_data)

    def save_to_csv(self, filename):
        df = self.to_dataframe()
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(df)} rows → {filename}")
        return df

    # ── Session / CSRF ─────────────────────────────────────────────────────────

    def _init_session(self):
        """GET the main page to collect cookies and CSRF token."""
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/147.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer":  PMI_SEARCH_URL,
            "Origin":   PMI_BASE,
        })
        resp = self._session.get(PMI_SEARCH_URL, timeout=20)
        resp.raise_for_status()
        self._csrf = self._parse_csrf(resp.text)
        logger.info(
            f"Session ready  |  "
            f"cookies: {list(self._session.cookies.keys())}  |  "
            f"CSRF: {(self._csrf or 'NOT FOUND')[:12]}…"
        )

    def _parse_csrf(self, html):
        """Extract _csrf value from a page or fragment."""
        soup = BeautifulSoup(html, "html.parser")
        tag  = soup.find("meta", {"name": "_csrf"})
        if tag and tag.get("content"):
            return tag["content"]
        inp = soup.find("input", {"name": "_csrf", "type": "hidden"})
        if inp and inp.get("value"):
            return inp["value"]
        return None

    # ── District label discovery ───────────────────────────────────────────────

    def _fetch_district_labels(self):
        """
        Try to GET the location popup and parse the postal district labels.
        Returns a list of strings, or [] on failure.
        """
        try:
            resp = self._session.get(PMI_POPUP_URL, timeout=15)
            resp.raise_for_status()
            soup   = BeautifulSoup(resp.text, "html.parser")
            labels = []
            # District labels appear as option values or li/label text
            # containing the "D01 / ..." pattern
            for el in soup.find_all(string=True):
                text = el.strip()
                if text and text.startswith("D") and " / " in text:
                    import re
                    if re.match(r"D\d{2} /", text):
                        labels.append(text)
            return labels if len(labels) >= 20 else []
        except Exception as exc:
            logger.debug(f"Popup fetch failed: {exc}")
            return []

    # ── CSV download ───────────────────────────────────────────────────────────

    def _build_download_payload(self, district_label, ptype_id):
        """
        Build the form payload for the CSV download endpoint.
        Mirrors the exact field order from the confirmed live cURL.
        """
        location_json = json.dumps(["postalDistrict", district_label])
        return [
            ("resultPerPage",          "20"),
            ("displayResult",          "true"),
            ("displayResultHeader",    "1"),
            ("loadAnalysis",           "true"),
            ("displayAnalysis",        "0"),
            ("displayChart",           "true"),
            ("displayAnalysisFilters", "true"),
            ("dashboardDisplay",       "false"),
            ("panelNo",                ""),
            ("panelId",                ""),
            ("panelName",              ""),
            ("locationDetails",        location_json),
            ("saleYearFrom",           "2021"),
            ("saleMonthFrom",          "5"),
            ("saleYearTo",             "2026"),
            ("saleMonthTo",            "5"),
            ("propertyTypeGroupNo",    str(ptype_id)),
            ("transactedPriceFrom",    ""),
            ("transactedPriceTo",      ""),
            ("pricePerUnitAreaFrom",   ""),
            ("pricePerUnitAreaTo",     ""),
            ("pricePerUnitAreaUOM",    "PSF"),
            ("areaFrom",               ""),
            ("areaTo",                 ""),
            ("areaUOM",                "SQM"),
            ("blockHouseNumber",       ""),
            ("levelFrom",              ""),
            ("levelTo",                ""),
            ("unitNumberFrom",         ""),
            ("unitNumberTo",           ""),
            ("typeofAreaLand",         ""),
            ("typeofAreaStrata",       ""),
            ("enblocYes",              ""),
            ("enblocNo",               ""),
            ("page",                   "0"),
            ("gotoPage",               "1"),
            ("tableDisplay",           "collapseColumn"),
            ("sortBy",                 "5"),
            ("sortAsc",                "0"),
            ("downloadType",           "downloadCSV"),
            ("variableNo",             ""),
            ("dataSet1No",             ""),
            ("dataSet2No",             ""),
            # Select all 17 columns
            *[("selectColumn", str(i)) for i in range(1, 18)],
            ("_selectColumn",          "1"),
            ("_csrf",                  self._csrf or ""),
        ]

    def _download_csv(self, district_label, ptype_id):
        """
        POST to the download endpoint and return a parsed DataFrame.
        Returns None if the response is not a valid CSV.
        """
        headers = {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Content-Type":              "application/x-www-form-urlencoded",
            "Sec-Fetch-Dest":            "document",
            "Sec-Fetch-Mode":            "navigate",
            "Sec-Fetch-Site":            "same-origin",
            "Sec-Fetch-User":            "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        payload = self._build_download_payload(district_label, ptype_id)

        resp = self._session.post(
            PMI_DOWNLOAD_URL,
            data=payload,
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()

        # Update CSRF token if the response contains one
        new_csrf = self._parse_csrf(resp.text)
        if new_csrf:
            self._csrf = new_csrf

        content_type = resp.headers.get("Content-Type", "")
        logger.debug(
            f"  Download response: status={resp.status_code}, "
            f"content-type={content_type}, len={len(resp.content)} bytes"
        )

        # Expect a CSV file (text/csv or attachment)
        if "text/csv" in content_type or "attachment" in resp.headers.get("Content-Disposition", ""):
            return self._parse_csv_response(resp.text, district_label, ptype_id)

        # Server sometimes returns CSV as text/html — try parsing anyway
        if resp.text.strip().startswith(("Project Name", "\"Project Name")):
            return self._parse_csv_response(resp.text, district_label, ptype_id)

        # Not a CSV — log snippet for debugging
        snippet = resp.text[:500].replace("\n", " ").strip()
        logger.warning(f"  Unexpected response (not CSV): {snippet}")
        return None

    def _parse_csv_response(self, text, district_label, ptype_id):
        """Parse the CSV text and return a cleaned DataFrame."""
        try:
            df = pd.read_csv(StringIO(text))
            if df.empty:
                return df

            # Normalise column names to snake_case
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(r"[\s\(\)\$]+", "_", regex=True)
                .str.replace(r"_+", "_", regex=True)
                .str.strip("_")
            )

            # Stamp district label if column not present
            if "postal_district" not in df.columns:
                # Extract just the D-number (e.g. "1" from "D01 / ...")
                num = district_label.split("/")[0].strip().lstrip("D").lstrip("0") or "0"
                df["postal_district"] = num

            return df
        except Exception as exc:
            logger.warning(f"  CSV parse failed: {exc}")
            return None


# ── Alias ──────────────────────────────────────────────────────────────────────

URAPMITransactionScraper = URARealestateScraper


# ── Standalone usage ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    scraper = URARealestateScraper()

    # Test with first 2 districts (D01, D02) and Apartments only
    df = scraper.scrape(districts=[0, 1], property_type_ids=["3"])

    print(f"\nTotal records: {len(df)}")
    if not df.empty:
        print(f"Columns: {list(df.columns)}")
        print(df.head(5).to_string())
        out = Path("data/raw/ura_pmi_test.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        print(f"\nSaved → {out}")
    else:
        print("No data — check logs above")
