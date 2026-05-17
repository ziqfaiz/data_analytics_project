"""
geocode_hospitals.py
--------------------
Enriches data/raw/hospitals.csv with latitude and longitude by querying the
Singapore Land Authority's OneMap API, then writes the result to
data/enriched/hospitals.csv.

OneMap API docs: https://www.onemap.gov.sg/apidocs/
No API key is required for the search endpoint.

Usage:
    python scripts/geocode_hospitals.py
"""

import time
import logging
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RAW_CSV = Path(__file__).parent.parent / "data" / "raw" / "hospitals.csv"
OUT_DIR = Path(__file__).parent.parent / "data" / "enriched"
OUT_CSV = OUT_DIR / "hospitals.csv"

ONEMAP_URL = "https://www.onemap.gov.sg/api/common/elastic/search"

# Seconds to wait between API requests — be a polite citizen
REQUEST_DELAY = 0.4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# OneMap geocoding
# ---------------------------------------------------------------------------

def _query_onemap(search_val: str) -> dict | None:
    """
    Hit the OneMap search endpoint and return the best result dict,
    or None if nothing was found.
    """
    params = {
        "searchVal": search_val,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": 1,
    }
    try:
        resp = requests.get(ONEMAP_URL, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return results[0] if results else None
    except requests.RequestException as exc:
        log.warning(f"Request failed for '{search_val}': {exc}")
        return None


def _fallback_queries(name: str) -> list[str]:
    """
    Generate progressively simpler search strings to try when the full name
    returns no results.

    Strategy
    --------
    1. Name + "Singapore"           e.g. "Changi General Hospital Singapore"
    2. Name alone                   e.g. "Changi General Hospital"
    3. Drop trailing type word      e.g. "Changi General"
    4. First two words + Singapore  e.g. "Changi General Singapore"
    """
    trailing_words = {"hospital", "centre", "center", "medical", "health"}
    words = name.split()

    queries = [
        f"{name} Singapore",
        name,
    ]

    # Strip last word if it's a generic type word
    if words and words[-1].lower() in trailing_words:
        shorter = " ".join(words[:-1])
        queries.append(shorter)
        queries.append(f"{shorter} Singapore")

    # First two meaningful words
    if len(words) >= 2:
        two_words = " ".join(words[:2])
        queries.append(f"{two_words} Singapore")

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    return unique


def geocode_hospital(name: str) -> tuple[float | None, float | None, str]:
    """
    Return (latitude, longitude, matched_address) for a hospital name.
    Tries multiple query variations before giving up.
    """
    for query in _fallback_queries(name):
        result = _query_onemap(query)
        time.sleep(REQUEST_DELAY)

        if result:
            lat = float(result["LATITUDE"])
            lng = float(result["LONGITUDE"])
            address = result.get("ADDRESS", "")
            log.info(f"  ✓  {name!r:<45}  →  {lat:.6f}, {lng:.6f}  [{address}]")
            return lat, lng, address

    log.warning(f"  ✗  No result found for {name!r}")
    return None, None, ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Ensure output directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_CSV)
    log.info(f"Loaded {len(df)} hospitals from {RAW_CSV}")

    # Cache results by name so duplicates (e.g. "Woodlands Hospital" appearing
    # as both Acute and Community) only make one API call
    coord_cache: dict[str, tuple] = {}

    lats, lngs, addresses = [], [], []

    for _, row in df.iterrows():
        name = row["name"]

        if name in coord_cache:
            lat, lng, addr = coord_cache[name]
            log.info(f"  ↩  {name!r} (cached)  →  {lat}, {lng}")
        else:
            lat, lng, addr = geocode_hospital(name)
            coord_cache[name] = (lat, lng, addr)

        lats.append(lat)
        lngs.append(lng)
        addresses.append(addr)

    df["latitude"] = lats
    df["longitude"] = lngs
    df["matched_address"] = addresses   # handy for spot-checking accuracy

    df.to_csv(OUT_CSV, index=False)
    log.info(f"\nSaved enriched data → {OUT_CSV}")

    # Summary
    filled = df["latitude"].notna().sum()
    total = len(df)
    log.info(f"Geocoded {filled}/{total} hospitals successfully.")

    if filled < total:
        missing = df[df["latitude"].isna()]["name"].tolist()
        log.warning(f"Missing coordinates for: {missing}")


if __name__ == "__main__":
    main()
