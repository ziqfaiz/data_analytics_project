# Quick Start Checklist

## Pre-Flight Checks

Before running the scrapers, verify your setup:

- [ ] Python 3.8 or higher installed
- [ ] `pip` package manager available
- [ ] Internet connection active
- [ ] `requirements.txt` in project directory
- [ ] `scrapers/` directory exists
- [ ] `main.py` file present

## Installation (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation (should show no errors)
python test_scrapers.py

# 3. Check output
# You should see: ✓ ALL TESTS PASSED!
```

## Run All Scrapers (3-5 minutes)

```bash
# 1. Execute main script
python main.py

# 2. Wait for completion
# You should see progress messages for each scraper

# 3. Check results
ls -la data/raw/
# Should show: mrt_stations.csv, hospitals.csv, schools.csv, ura_realestate.csv
```

## Run Individual Scrapers

```bash
# MRT Stations (30-45 seconds)
python scrapers/mrt_scraper.py

# Hospitals (20-30 seconds)
python scrapers/hospitals_scraper.py

# Schools (90-120 seconds)
python scrapers/schools_scraper.py

# URA Real Estate (45-60 seconds)
python scrapers/ura_realestate_scraper.py
```

## Verify Output

```bash
# Check file sizes
du -h data/raw/*.csv

# View first few rows
head -5 data/raw/mrt_stations.csv
head -5 data/raw/hospitals.csv
head -5 data/raw/schools.csv
head -5 data/raw/ura_realestate.csv

# Count records
wc -l data/raw/*.csv
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'selenium'"
**Solution:** Run `pip install -r requirements.txt`

### Problem: "Unable to obtain driver for chrome"
**Solution:** Install ChromeDriver: `pip install chromedriver-binary`

### Problem: Empty CSV files
**Solution:** 
1. Check internet connection
2. Run with debug logging
3. Verify websites are accessible in browser

### Problem: Timeout errors
**Solution:** Increase wait time when initializing scraper with `implicit_wait=20`

## Next Steps

1. ✓ **Run All Scrapers** → `python main.py`
2. ✓ **Inspect Output** → Check `data/raw/` directory
3. ✓ **Load Data** → Use pandas
4. ✓ **Analyze Data** → Perform exploratory data analysis
5. ✓ **Build Models** → Create predictions or visualizations

## Documentation

- **Setup Guide:** `SCRAPER_SETUP_GUIDE.md`
- **Project Status:** `PROJECT_STATUS.md`

---

**Ready to start?** Run: `python main.py`
