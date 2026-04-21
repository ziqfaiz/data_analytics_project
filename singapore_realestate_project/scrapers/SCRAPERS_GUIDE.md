# Singapore Data Scrapers - Quick Reference Guide

## Overview

Your scrapers directory now contains **8 web scrapers** for collecting Singapore-related data for your data analysis project.

---

## All Available Scrapers

### 1. **MRT Stations Scraper** 🚆
- **File:** `mrt_scraper.py`
- **Source:** Wikipedia - List of Singapore MRT stations
- **URL:** https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations
- **Data Extracted:**
  - Station name, Station code, MRT line, Opening year, Coordinates
- **Output:** `mrt_stations.csv`

```python
from scrapers import MRTScraper
scraper = MRTScraper(headless=True)
df = scraper.scrape("https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations")
scraper.save_to_csv("data/raw/mrt_stations.csv")
```

---

### 2. **Schools Scraper** 🏫
- **File:** `schools_scraper.py`
- **Source:** MOE SchoolFinder
- **URL:** https://www.moe.gov.sg/schoolfinder
- **Data Extracted:**
  - School name, Type (preschool/primary/secondary/college/JC), Address, Contact, Principal, Website
- **Output:** `schools.csv`

```python
from scrapers import SchoolsScraper
scraper = SchoolsScraper(headless=True)
df = scraper.scrape(
    "https://www.moe.gov.sg/schoolfinder",
    school_types=['primary', 'secondary', 'college']
)
scraper.save_to_csv("data/raw/schools.csv")
```

---

### 3. **Hospitals Scraper** 🏥
- **File:** `hospitals_scraper.py`
- **Source:** SGDI
- **URL:** https://www.sgdi.gov.sg/other-organisations/hospitals
- **Data Extracted:**
  - Hospital name, Address, Contact, Specialties, Bed count, Website
- **Output:** `hospitals.csv`

```python
from scrapers import HospitalsScraper
scraper = HospitalsScraper(headless=True)
df = scraper.scrape("https://www.sgdi.gov.sg/other-organisations/hospitals")
scraper.save_to_csv("data/raw/hospitals.csv")
```

---

### 4. **URA Real Estate Scraper** 🏢
- **File:** `ura_realestate_scraper.py`
- **Source:** URA Property Data Portal
- **URL:** https://www.ura.gov.sg/Corporate/Property/Property-Data
- **Data Extracted:**
  - Property type, Location, Price, Rental, Supply, Vacancy, Stock, Pipeline supply, Time period
- **Output:** `ura_realestate.csv`

```python
from scrapers import URARealestateScraper
scraper = URARealestateScraper(headless=True)
df = scraper.scrape(
    "https://www.ura.gov.sg/Corporate/Property/Property-Data",
    property_types=['residential', 'commercial']
)
scraper.save_to_csv("data/raw/ura_realestate.csv")
```

---

### 5. **PropertyGuru Scraper** 💰
- **File:** `propertyguru_scraper.py`
- **Source:** PropertyGuru Singapore
- **URL:** https://www.propertyguru.com.sg/
- **Data Extracted:**
  - Price, Location, Property type, Floor area, Bedrooms, Property URL
- **Output:** `propertyguru_listings.csv`

```python
from scrapers import PropertyGuruScraper
scraper = PropertyGuruScraper(headless=True)
df = scraper.scrape(
    "https://www.propertyguru.com.sg/property-for-sale",
    max_pages=5
)
scraper.save_to_csv("data/raw/propertyguru_listings.csv")
```

---

### 6. **EdgeProp Scraper** 💰
- **File:** `edgeprop_scraper.py`
- **Source:** EdgeProp Singapore
- **URL:** https://www.edgeprop.sg/
- **Data Extracted:**
  - Price, Location, Property type, Floor area, Bedrooms, Property URL
- **Output:** `edgeprop_listings.csv`

```python
from scrapers import EdgePropScraper
scraper = EdgePropScraper(headless=True)
df = scraper.scrape(
    "https://www.edgeprop.sg/property/search/residential",
    max_pages=5
)
scraper.save_to_csv("data/raw/edgeprop_listings.csv")
```

---

## Using ScraperManager (Recommended)

The `ScraperManager` class orchestrates all scrapers in one place:

### Quick Start:
```python
from scrapers import ScraperManager

# Create manager
manager = ScraperManager(output_dir="data/raw")

# Scrape each source
mrt_df = manager.scrape_mrt_stations(
    "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"
)
schools_df = manager.scrape_schools(
    "https://www.moe.gov.sg/schoolfinder"
)
hospitals_df = manager.scrape_hospitals(
    "https://www.sgdi.gov.sg/other-organisations/hospitals"
)
ura_df = manager.scrape_ura_realestate(
    "https://www.ura.gov.sg/Corporate/Property/Property-Data"
)

# All files saved to data/raw/
# - mrt_stations.csv
# - schools.csv
# - hospitals.csv
# - ura_realestate.csv
```

---

## Data Categories

### Infrastructure & Services
| Source | Type | Records | Format |
|--------|------|---------|--------|
| MRT Stations | Transport | ~190 | CSV |
| Schools | Education | ~1000+ | CSV |
| Hospitals | Healthcare | ~20+ | CSV |

### Real Estate
| Source | Type | Property Types | Format |
|--------|------|---|--------|
| PropertyGuru | Private Listings | Residential | CSV |
| EdgeProp | Private Listings | Residential | CSV |
| URA | Official Data | Residential, Commercial | CSV |

---

## Important Notes

### Before You Scrape:
1. ✅ Check website `robots.txt` and Terms of Service
2. ✅ Add delays between requests (already implemented)
3. ✅ Use reasonable `max_pages` limits for testing
4. ✅ Monitor for blocked access or timeouts

### CSS Selectors:
- Scrapers use CSS/XPath selectors that may change if websites update
- If a scraper fails, website structure may have changed
- You'll need to update selectors in the scraper file
- Use browser DevTools (F12) to find correct selectors

### Output Files:
- All CSV files are saved to `data/raw/` by default
- Can change output directory via `ScraperManager(output_dir="...")`
- Columns vary by scraper (see README.md for details)

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Timeout error | Increase `implicit_wait` in scraper init |
| No elements found | Website structure may have changed, update CSS selectors |
| Blocked by website | Add delays, check robots.txt, consider contacting site owner |
| WebDriver not found | Install ChromeDriver or use webdriver-manager |
| Memory errors | Reduce `max_pages` or use `headless=True` |

---

## Next Steps

1. **Test each scraper individually** with small datasets
2. **Verify the CSS selectors** match current website structure
3. **Set up scheduled scraping** for periodic data collection
4. **Store data in database** instead of just CSV for production
5. **Monitor scraper logs** for failures and selector mismatches
6. **Update selectors** as websites evolve

---

## File Structure
```
singapore_realestate_project/
└── scrapers/
    ├── base_scraper.py              # Base class (do not modify)
    ├── mrt_scraper.py               # NEW: MRT stations
    ├── schools_scraper.py           # NEW: Schools
    ├── hospitals_scraper.py         # NEW: Hospitals
    ├── ura_realestate_scraper.py    # NEW: URA real estate
    ├── propertyguru_scraper.py      # PropertyGuru listings
    ├── edgeprop_scraper.py          # EdgeProp listings
    ├── scraper_manager.py           # Manager class (updated)
    ├── __init__.py                  # Module init (updated)
    ├── README.md                    # Detailed documentation (updated)
    └── SCRAPERS_GUIDE.md            # This file
```

---

## For More Information
- Read `README.md` for detailed documentation
- Check individual scraper files for implementation details
- See `base_scraper.py` for inherited methods and utilities
- Review example usage in `scraper_manager.py` main section

Happy scraping! 🎉
