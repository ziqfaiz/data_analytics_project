# Web Scrapers Module

This module contains Selenium-based scrapers for collecting data from various Singapore sources including property portals, transport infrastructure, education, and healthcare data.

## Structure

```
scrapers/
├── __init__.py                    # Module initialization
├── base_scraper.py               # Base class for all scrapers
├── propertyguru_scraper.py       # PropertyGuru property portal scraper
├── edgeprop_scraper.py           # EdgeProp property portal scraper
├── mrt_scraper.py                # Singapore MRT stations scraper
├── schools_scraper.py            # Singapore schools scraper
├── hospitals_scraper.py          # Singapore hospitals scraper
├── ura_realestate_scraper.py     # URA real estate data scraper
├── scraper_manager.py            # Orchestrates multiple scrapers
└── README.md                     # This file
```

## Components

### BaseScraper
Base class providing common Selenium functionality:
- WebDriver setup/teardown
- Element waiting and finding
- Safe text/attribute extraction
- Screenshot capture
- Data export (CSV, DataFrame)

**Key Methods:**
- `setup_driver()` - Initialize Chrome WebDriver
- `get_page(url)` - Navigate to URL
- `wait_for_element()` - Wait for element to load
- `extract_text()` - Safely extract text
- `scroll_to_bottom()` - Scroll page
- `to_dataframe()` - Convert to pandas DataFrame
- `save_to_csv()` - Export results

### PropertyGuruScraper
Scraper for PropertyGuru Singapore (www.propertyguru.com.sg)

**Features:**
- Multi-page scraping
- Extracts: price, location, property type, floor area, bedrooms
- Pagination handling
- Property URL capture

**Usage:**
```python
from scrapers import PropertyGuruScraper

scraper = PropertyGuruScraper(headless=True)
url = "https://www.propertyguru.com.sg/property-for-sale"
df = scraper.scrape(url, max_pages=5)
df.to_csv("propertyguru_listings.csv")
```

### EdgePropScraper
Scraper for EdgeProp Singapore (www.edgeprop.sg)

**Features:**
- Multi-page scraping
- Extracts: price, location, property type, floor area, bedrooms
- Pagination handling
- Similar interface to PropertyGuruScraper

**Usage:**
```python
from scrapers import EdgePropScraper

scraper = EdgePropScraper(headless=True)
url = "https://www.edgeprop.sg/property/search/residential"
df = scraper.scrape(url, max_pages=5)
df.to_csv("edgeprop_listings.csv")
```

### MRTScraper
Scraper for Singapore MRT station data from Wikipedia

**Features:**
- Extracts MRT station information from Wikipedia tables
- Data: station name, line, code, opening year, coordinates
- Handles multiple MRT lines
- Coordinate extraction from Wikipedia

**Usage:**
```python
from scrapers import MRTScraper

scraper = MRTScraper(headless=True)
url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"
df = scraper.scrape(url)
df.to_csv("mrt_stations.csv")
print(f"Extracted {len(df)} MRT stations")
```

**Output Columns:**
- `name`: Station name
- `code`: Station code (e.g., NS1, EW1)
- `line`: MRT line (e.g., NS, EW, NE, CC, DT, TE)
- `opening_year`: Year the station opened
- `latitude`: Station latitude coordinate
- `longitude`: Station longitude coordinate

### SchoolsScraper
Scraper for Singapore schools from MOE SchoolFinder

**Features:**
- Scrapes schools by type (preschool, primary, secondary, college, JC)
- Extracts: school name, type, address, contact, principal
- Handles pagination and dynamic loading
- Support for multiple school categories

**Usage:**
```python
from scrapers import SchoolsScraper

scraper = SchoolsScraper(headless=True)
url = "https://www.moe.gov.sg/schoolfinder"

# Scrape specific school types
df = scraper.scrape(url, school_types=['primary', 'secondary'])
df.to_csv("schools.csv")

# Scrape all school types
df_all = scraper.scrape(url)
```

**Output Columns:**
- `name`: School name
- `type`: School type (preschool, primary, secondary, college, jc)
- `address`: School address
- `contact`: Contact information
- `principal`: Principal name (if available)
- `url`: School website URL

### HospitalsScraper
Scraper for Singapore hospitals from SGDI

**Features:**
- Extracts hospital information from SGDI website
- Data: hospital name, address, contact, specialties, bed count
- Handles dynamic content loading
- Pattern matching for bed count extraction

**Usage:**
```python
from scrapers import HospitalsScraper

scraper = HospitalsScraper(headless=True)
url = "https://www.sgdi.gov.sg/other-organisations/hospitals"
df = scraper.scrape(url)
df.to_csv("hospitals.csv")
print(f"Extracted {len(df)} hospitals")
```

**Output Columns:**
- `name`: Hospital name
- `address`: Hospital address
- `contact`: Contact number
- `specialties`: Medical specialties offered
- `bed_count`: Number of beds
- `url`: Hospital website URL

### URARealestateScraper
Scraper for Singapore real estate property data from URA

**Features:**
- Scrapes property data from URA Property Data portal
- Support for residential and commercial properties
- Extracts: location, price, rental, supply, vacancy, stock data
- Pipeline supply data for new developments
- Quarterly/period data tracking

**Usage:**
```python
from scrapers import URARealestateScraper

scraper = URARealestateScraper(headless=True)
url = "https://www.ura.gov.sg/Corporate/Property/Property-Data"

# Scrape both residential and commercial
df = scraper.scrape(url, property_types=['residential', 'commercial'])
df.to_csv("ura_realestate.csv")

# Scrape specific type
df_res = scraper.scrape(url, property_types=['residential'])
```

**Output Columns:**
- `property_type`: Type of property (residential/commercial)
- `location`: Location/district
- `price`: Price information
- `rental`: Rental information
- `supply`: Total supply
- `vacancy`: Vacancy rate
- `stock`: Stock information
- `pipeline_supply`: Pipeline supply for new projects
- `year`: Time period of data

### ScraperManager
Orchestrates multiple scrapers and combines results

**Features:**
- Run multiple scrapers sequentially
- Combine results from different sources
- Generate statistics
- Automatic CSV export

**Usage:**
```python
from scrapers import ScraperManager

manager = ScraperManager(output_dir="data/raw")

# Scrape PropertyGuru
pg_df = manager.scrape_propertyguru(pg_url, max_pages=5)

# Scrape EdgeProp
ep_df = manager.scrape_edgeprop(ep_url, max_pages=5)

# Combine results
combined = manager.combine_results()

# View statistics
manager.print_statistics()
```

## Quick Start

### 1. Scrape Property Listings (PropertyGuru)
```python
from scrapers import PropertyGuruScraper

scraper = PropertyGuruScraper()
df = scraper.scrape("https://www.propertyguru.com.sg/property-for-sale", max_pages=3)
print(f"Scraped {len(df)} properties")
df.to_csv("properties.csv")
```

### 2. Scrape MRT Stations
```python
from scrapers import MRTScraper

scraper = MRTScraper(headless=True)
url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"
df = scraper.scrape(url)
print(f"Scraped {len(df)} MRT stations")
df.to_csv("mrt_stations.csv")
```

### 3. Scrape Schools
```python
from scrapers import SchoolsScraper

scraper = SchoolsScraper(headless=True)
url = "https://www.moe.gov.sg/schoolfinder"
df = scraper.scrape(url, school_types=['primary', 'secondary'])
print(f"Scraped {len(df)} schools")
df.to_csv("schools.csv")
```

### 4. Multi-Source Scraping with Manager
```python
from scrapers import ScraperManager

manager = ScraperManager(output_dir="data/raw")

# Scrape all sources
mrt_df = manager.scrape_mrt_stations("https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations")
schools_df = manager.scrape_schools("https://www.moe.gov.sg/schoolfinder")
hospitals_df = manager.scrape_hospitals("https://www.sgdi.gov.sg/other-organisations/hospitals")
ura_df = manager.scrape_ura_realestate("https://www.ura.gov.sg/Corporate/Property/Property-Data")

# All data saved to data/raw/ directory
```

### 5. Custom Scraper
Extend BaseScraper for other portals:

```python
from scrapers import BaseScraper
from selenium.webdriver.common.by import By

class CustomScraper(BaseScraper):
    def scrape(self, url, max_pages=5):
        self.setup_driver()
        try:
            self.get_page(url)
            # Your custom scraping logic here
            return self.to_dataframe()
        finally:
            self.close_driver()
```

## Important Notes

### CSS Selectors
The selectors in PropertyGuruScraper and EdgePropScraper are TEMPLATES and need to be updated based on the actual HTML structure of each website. 

**To find correct selectors:**
1. Open website in browser
2. Right-click on property listing
3. Select "Inspect Element"
4. Find the appropriate CSS selectors for each field
5. Update the selectors in the scraper

### Example: Finding Price Selector
```python
# In developer tools, find the price element
# e.g., <span class="price">$500,000</span>

# Update the selector in _extract_price():
price_text = self.extract_text(card, By.CSS_SELECTOR, ".price", "")
```

### Legal Considerations
- Always check website's `robots.txt` and Terms of Service
- Add delays between requests to avoid overloading servers
- Respect `Robots.txt` rules
- Consider contacting website owner for permission
- Use responsibly

### Performance Tips
1. Use `headless=True` for faster scraping
2. Set reasonable `implicit_wait` (default 10s)
3. Limit `max_pages` for testing
4. Use logging to monitor progress
5. Combine screenshots for debugging

## Troubleshooting

### WebDriver Issues
```
ERROR: Failed to initialize WebDriver
→ Install ChromeDriver: https://chromedriver.chromium.org/
→ Or use webdriver-manager: pip install webdriver-manager
```

### Selector Not Found
```
ERROR: No elements found
→ Check website structure (may have changed)
→ Update CSS selectors in scraper
→ Use browser DevTools to find correct selectors
```

### Timeout Errors
```
ERROR: Timeout waiting for element
→ Increase wait time
→ Check if element is lazy-loaded
→ Add scroll before extraction
```

### Blocked by Website
```
ERROR: 403 Forbidden
→ Add user-agent header (already in BaseScraper)
→ Increase delays between requests
→ Try without headless mode (for debugging)
```

## Example: Using in Data Collection Pipeline

### Example 1: Scrape All Infrastructure Data

```python
# scripts/data_collection.py

from scrapers import ScraperManager
import logging

logging.basicConfig(level=logging.INFO)

def scrape_singapore_infrastructure():
    """Scrape Singapore transport, education, and healthcare data"""
    manager = ScraperManager(output_dir="data/raw")

    # MRT Stations
    mrt_url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"
    mrt_df = manager.scrape_mrt_stations(mrt_url)

    # Schools
    schools_url = "https://www.moe.gov.sg/schoolfinder"
    schools_df = manager.scrape_schools(schools_url, school_types=['primary', 'secondary', 'college'])

    # Hospitals
    hospitals_url = "https://www.sgdi.gov.sg/other-organisations/hospitals"
    hospitals_df = manager.scrape_hospitals(hospitals_url)

    return {
        'mrt': mrt_df,
        'schools': schools_df,
        'hospitals': hospitals_df
    }

# Usage
if __name__ == "__main__":
    data = scrape_singapore_infrastructure()
    print(f"MRT Stations: {len(data['mrt'])}")
    print(f"Schools: {len(data['schools'])}")
    print(f"Hospitals: {len(data['hospitals'])}")
```

### Example 2: Scrape Property Data (Private + URA)

```python
# scripts/data_collection.py

from scrapers import ScraperManager

def scrape_singapore_properties():
    """Scrape both private properties and URA official data"""
    manager = ScraperManager(output_dir="data/raw")

    # Private Properties
    pg_url = "https://www.propertyguru.com.sg/property-for-sale?market=residential"
    manager.scrape_propertyguru(pg_url, max_pages=10)

    ep_url = "https://www.edgeprop.sg/property/search/residential"
    manager.scrape_edgeprop(ep_url, max_pages=10)

    # URA Official Data
    ura_url = "https://www.ura.gov.sg/Corporate/Property/Property-Data"
    manager.scrape_ura_realestate(ura_url, property_types=['residential', 'commercial'])

    # Combine and analyze
    combined_df = manager.combine_results()
    manager.print_statistics()

    return combined_df

# Usage
if __name__ == "__main__":
    df = scrape_singapore_properties()
    print(f"Total property records: {len(df)}")
```

### Example 3: Integrated Data Collection

```python
# scripts/data_collection.py

from scrapers import ScraperManager
import logging

logging.basicConfig(level=logging.INFO)

def scrape_all_singapore_data():
    """Comprehensive data collection for data analysis project"""
    manager = ScraperManager(output_dir="data/raw")

    print("=" * 60)
    print("Starting comprehensive Singapore data scrape...")
    print("=" * 60)

    # Infrastructure & Services
    print("\n[1/6] Scraping MRT stations...")
    mrt_df = manager.scrape_mrt_stations(
        "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"
    )

    print("\n[2/6] Scraping schools...")
    schools_df = manager.scrape_schools(
        "https://www.moe.gov.sg/schoolfinder",
        school_types=['primary', 'secondary', 'college']
    )

    print("\n[3/6] Scraping hospitals...")
    hospitals_df = manager.scrape_hospitals(
        "https://www.sgdi.gov.sg/other-organisations/hospitals"
    )

    # Real Estate Data
    print("\n[4/6] Scraping PropertyGuru listings...")
    pg_df = manager.scrape_propertyguru(
        "https://www.propertyguru.com.sg/property-for-sale?market=residential",
        max_pages=5
    )

    print("\n[5/6] Scraping EdgeProp listings...")
    ep_df = manager.scrape_edgeprop(
        "https://www.edgeprop.sg/property/search/residential",
        max_pages=5
    )

    print("\n[6/6] Scraping URA property data...")
    ura_df = manager.scrape_ura_realestate(
        "https://www.ura.gov.sg/Corporate/Property/Property-Data",
        property_types=['residential', 'commercial']
    )

    print("\n" + "=" * 60)
    print("Scraping completed!")
    print("=" * 60)

    return {
        'mrt': mrt_df,
        'schools': schools_df,
        'hospitals': hospitals_df,
        'propertyguru': pg_df,
        'edgeprop': ep_df,
        'ura': ura_df
    }

# Usage
if __name__ == "__main__":
    data = scrape_all_singapore_data()
```

## Implementation Status

✅ **Completed Scrapers:**
- ✓ MRT Stations (Wikipedia)
- ✓ Schools (MOE SchoolFinder)
- ✓ Hospitals (SGDI)
- ✓ URA Real Estate Data
- ✓ PropertyGuru (existing)
- ✓ EdgeProp (existing)

## Important Considerations

### For Each Scraper:
1. **Test selectors** on actual websites before production use
2. **Update CSS selectors** if website structure changes
3. **Monitor robots.txt** and Terms of Service for each site
4. **Add appropriate delays** between requests
5. **Check for JavaScript rendering** needs

### Key Websites' Notes:

**Wikipedia (MRT):**
- Static content, good for table extraction
- No rate limiting concerns
- Selectors are stable

**MOE SchoolFinder:**
- May use JavaScript rendering
- Dynamic content loading with pagination
- Requires element waiting

**SGDI (Hospitals):**
- Dynamic content loading
- May require scrolling to load all data
- Content layout may vary

**URA (Real Estate):**
- May have restricted data download
- Check site for official API
- Consider direct data portal access

**PropertyGuru & EdgeProp:**
- May detect and block automated access
- User-agent rotation recommended
- Session management important

## Next Steps & Recommendations

1. **Test each scraper** with small datasets
2. **Verify CSS selectors** match current website structure
3. **Set up robust error handling** for production use
4. **Implement retry logic** for network failures
5. **Add database storage** instead of just CSV
6. **Schedule periodic scraping** with task scheduler
7. **Monitor scraper performance** and update selectors as websites change
8. **Consider rate limiting** to be respectful to server load
9. **Implement logging** for debugging and monitoring
10. **Set up alerts** for scraper failures

---

For more information on Selenium, visit: https://selenium-python.readthedocs.io/
For web scraping best practices: https://robotstxt.org/
