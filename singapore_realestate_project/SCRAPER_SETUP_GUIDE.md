# Singapore Data Analytics Project - Scraper Setup Guide

## Overview

This guide documents all the web scrapers available in this project and how to use them. The project includes four main scrapers for collecting Singapore-specific data:

1. **MRT Scraper** - Singapore Mass Rapid Transit (MRT) station data
2. **Hospitals Scraper** - Singapore hospital information
3. **Schools Scraper** - Singapore school information
4. **URA Real Estate Scraper** - Singapore property data

---

## Quick Start

### Prerequisites

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `selenium==4.12.0` - Web automation
- `pandas==2.0.3` - Data manipulation
- `beautifulsoup4==4.12.2` - HTML parsing

### Running All Scrapers

To run all scrapers at once:

```bash
python main.py
```

This will scrape all data sources and save the results to `data/raw/` directory in CSV format.

### Running Individual Scrapers

Each scraper can be run independently:

```bash
# MRT Scraper
python scrapers/mrt_scraper.py

# Hospitals Scraper
python scrapers/hospitals_scraper.py

# Schools Scraper
python scrapers/schools_scraper.py

# URA Real Estate Scraper
python scrapers/ura_realestate_scraper.py
```

### Testing Setup

To verify all scrapers are correctly configured:

```bash
python test_scrapers.py
```

This will:
- ✓ Test all imports
- ✓ Verify scraper initialization
- ✓ Check data structures
- ✓ Display scraper summary

---

## Scraper Details

### 1. MRT Scraper

**Purpose:** Extract Singapore MRT station information

**Source:** Wikipedia - List of Singapore MRT stations  
**URL:** https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations

**Data Fields:**
- `name` - Station name (English)
- `code` - Station code (e.g., NS10, EW1)
- `line` - MRT line code (NS, EW, NE, CC, DT, TE, JR)
- `opening_year` - Year station opened
- `latitude` - Station latitude coordinate
- `longitude` - Station longitude coordinate

**Output File:** `data/raw/mrt_stations.csv`

**Key Features:**
- Handles Wikipedia's multi-language table structure
- Automatically detects English station names
- Extracts station codes and line information
- Maps line names to codes (e.g., "North-South Line" → "NS")

**Expected Output:**
- ~160+ MRT stations
- Columns: name, code, line, opening_year, latitude, longitude

**Usage Example:**

```python
from scrapers import MRTScraper

scraper = MRTScraper(headless=True)
url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"

df = scraper.scrape(url)
print(f"Scraped {len(df)} stations")
df.to_csv("mrt_stations.csv", index=False)
```

---

### 2. Hospitals Scraper

**Purpose:** Extract Singapore hospital information by type

**Source:** Wikipedia - List of hospitals in Singapore  
**URL:** https://en.wikipedia.org/wiki/List_of_hospitals_in_Singapore

**Data Fields:**
- `name` - Hospital name
- `type` - Hospital type (Acute, Community, Psychiatric)
- `opened` - Year hospital opened
- `district` - District/Region
- `ownership` - Hospital ownership (Public, Private, etc.)
- `beds` - Number of beds
- `staff` - Number of staff

**Output File:** `data/raw/hospitals.csv`

**Hospital Types Supported:**
- `acute` - Acute care hospitals
- `community` - Community hospitals
- `psychiatric` - Psychiatric hospitals

**Key Features:**
- Identifies hospital types from section headings
- Handles complex rowspan attributes in HTML tables
- Correctly maps column positions for rowspan cells
- Cleans Wikipedia reference markers from data

**Expected Output:**
- ~30-50 hospitals across all types
- Columns: name, type, opened, district, ownership, beds, staff

**Usage Example:**

```python
from scrapers import HospitalsScraper

scraper = HospitalsScraper(headless=True)
url = "https://en.wikipedia.org/wiki/List_of_hospitals_in_Singapore"

# Scrape specific hospital types
df = scraper.scrape(url, hospital_types=['acute', 'community'])
print(f"Scraped {len(df)} hospitals")
df.to_csv("hospitals.csv", index=False)
```

---

### 3. Schools Scraper

**Purpose:** Extract Singapore school information by type

**Source:** MOE SchoolFinder  
**URL:** https://www.moe.gov.sg/schoolfinder

**Data Fields:**
- `name` - School name
- `type` - School type (Preschool, Primary, Secondary, JC, College)
- `address` - School address
- `contact` - Contact information (phone/email)
- `principal` - Principal name (if available)
- `url` - School website URL

**Output File:** `data/raw/schools.csv`

**School Types Supported:**
- `preschool` - Preschools
- `primary` - Primary schools
- `secondary` - Secondary schools
- `jc` - Junior colleges
- `college` - Colleges/Polytechnics

**Key Features:**
- Handles MOE's dynamic school listing interface
- Automatically accepts cookie consent
- Scrolls and loads all results
- Flexible CSS selector patterns for robust extraction
- Tolerates page layout variations

**Expected Output:**
- Hundreds of schools across all types
- Columns: name, type, address, contact, principal, url

**Usage Example:**

```python
from scrapers import SchoolsScraper

scraper = SchoolsScraper(headless=True)
url = "https://www.moe.gov.sg/schoolfinder"

# Scrape specific school types
df = scraper.scrape(url, school_types=['primary', 'secondary'])
print(f"Scraped {len(df)} schools")
df.to_csv("schools.csv", index=False)
```

---

### 4. URA Real Estate Scraper

**Purpose:** Extract Singapore real estate property data

**Source:** URA (Urban Redevelopment Authority)  
**URL:** https://www.ura.gov.sg/Corporate/Property/Property-Data

**Data Fields:**
- `property_type` - Type of property (Residential, Commercial)
- `location` - Property location/district
- `price` - Price or median price
- `rental` - Rental price/yield
- `supply` - Total supply
- `vacancy` - Vacancy rate
- `stock` - Stock information
- `pipeline_supply` - Future pipeline supply
- `year` - Data year/quarter

**Output File:** `data/raw/ura_realestate.csv`

**Property Types Supported:**
- `residential` - Residential properties
- `commercial` - Commercial properties

**Key Features:**
- Extracts data from tabular format
- Intelligently maps columns based on headers
- Handles dynamic content loading
- Tolerates various table formats

**Expected Output:**
- Multiple property records across different time periods
- Columns: property_type, location, price, rental, supply, vacancy, stock, pipeline_supply, year

**Usage Example:**

```python
from scrapers import URARealestateScraper

scraper = URARealestateScraper(headless=True)
url = "https://www.ura.gov.sg/Corporate/Property/Property-Data"

# Scrape all property types
df = scraper.scrape(url, property_types=['residential', 'commercial'])
print(f"Scraped {len(df)} property records")
df.to_csv("ura_realestate.csv", index=False)
```

---

## Project Structure

```
singapore_realestate_project/
├── main.py                          # Main script to run all scrapers
├── test_scrapers.py                 # Test suite for all scrapers
├── SCRAPER_SETUP_GUIDE.md          # This file
├── requirements.txt                 # Python dependencies
├── data/
│   └── raw/                         # Output CSV files
│       ├── mrt_stations.csv
│       ├── hospitals.csv
│       ├── schools.csv
│       └── ura_realestate.csv
└── scrapers/
    ├── __init__.py                  # Scraper module exports
    ├── base_scraper.py              # Base class for all scrapers
    ├── mrt_scraper.py               # MRT stations scraper
    ├── hospitals_scraper.py          # Hospitals scraper
    ├── schools_scraper.py            # Schools scraper
    ├── ura_realestate_scraper.py    # URA real estate scraper
    ├── propertyguru_scraper.py      # Property portal scraper
    ├── edgeprop_scraper.py          # Property portal scraper
    ├── scraper_manager.py            # Manager class for all scrapers
    ├── README.md                     # Scraper module documentation
    └── SCRAPERS_GUIDE.md            # Quick reference guide
```

---

## Common Issues & Troubleshooting

### Issue: "Unable to obtain driver for chrome"

**Problem:** ChromeDriver not found or incompatible with system

**Solution:**
1. Install/update Chrome browser
2. Install compatible ChromeDriver:
   ```bash
   pip install chromedriver-binary
   ```
3. Or use Selenium's webdriver-manager:
   ```bash
   pip install webdriver-manager
   ```

### Issue: Empty CSV files after scraping

**Problem:** Scrapers ran but produced no data

**Solutions:**
1. Check your internet connection
2. Verify the target websites are accessible
3. Check logs for CSS selector errors
4. Try running individual scraper with debug logging:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

### Issue: SSL Certificate errors

**Problem:** SSL verification fails when accessing HTTPS sites

**Solution:** Set environment variable before running:
```bash
export PYTHONHTTPSVERIFY=0  # Use with caution!
python main.py
```

### Issue: Timeout errors

**Problem:** Scraper times out waiting for page elements

**Solution:** Increase implicit wait time:
```python
scraper = MRTScraper(headless=True, implicit_wait=20)  # 20 seconds
```

---

## Best Practices

### 1. **Check Before Running**
Always verify websites are accessible before scraping:
```bash
# Test website connectivity
curl -I https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations
```

### 2. **Use Appropriate Wait Times**
- Default: 10 seconds
- Dynamic sites (MOE, URA): 15-20 seconds
- Adjust based on your internet speed

### 3. **Handle Errors Gracefully**
```python
try:
    df = scraper.scrape(url)
except Exception as e:
    logger.error(f"Scraping failed: {e}")
    # Handle error appropriately
```

### 4. **Check Data Quality**
Always inspect the output:
```python
df = scraper.scrape(url)
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print(df.head(10))
print(df.isnull().sum())  # Check for missing data
```

### 5. **Respect Websites**
- Don't make excessive requests
- Use reasonable delays between requests
- Follow robots.txt guidelines
- Check website terms of service

---

## Data Integration

### Combining Data Sources

Once you have all CSV files, you can combine them for analysis:

```python
import pandas as pd

# Load all data
mrt_df = pd.read_csv('data/raw/mrt_stations.csv')
hospitals_df = pd.read_csv('data/raw/hospitals.csv')
schools_df = pd.read_csv('data/raw/schools.csv')
property_df = pd.read_csv('data/raw/ura_realestate.csv')

# Combine or analyze as needed
print(f"Total MRT stations: {len(mrt_df)}")
print(f"Total hospitals: {len(hospitals_df)}")
print(f"Total schools: {len(schools_df)}")
print(f"Total property records: {len(property_df)}")
```

---

## Performance Tips

1. **Use Headless Mode** (default) - Faster than GUI mode
2. **Disable Images** - Reduce bandwidth usage
3. **Run in Parallel** - Use Python's multiprocessing for multiple scrapers
4. **Cache Results** - Check if CSV exists before scraping (main.py does this)

---

## Support & Documentation

For more information:
- **Scrapers Guide**: See `scrapers/SCRAPERS_GUIDE.md`
- **Base Scraper Docs**: See `scrapers/README.md`
- **Selenium Docs**: https://selenium-python.readthedocs.io/

---

## Changelog

### Version 1.0
- ✓ MRT Scraper - Implemented with Wikipedia table parsing
- ✓ Hospitals Scraper - Implemented with rowspan handling
- ✓ Schools Scraper - Implemented with MOE SchoolFinder support
- ✓ URA Real Estate Scraper - Implemented with dynamic data loading
- ✓ Test Suite - Comprehensive test coverage
- ✓ Documentation - Full setup and usage guides

---

**Last Updated:** April 28, 2026  
**Project Status:** Active Development
