"""
Test script to verify all scrapers are working correctly
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all scrapers can be imported"""
    print("\n" + "=" * 70)
    print("TESTING SCRAPER IMPORTS")
    print("=" * 70)

    try:
        from scrapers import (
            BaseScraper,
            MRTScraper,
            HospitalsScraper,
            SchoolsScraper,
            URARealestateScraper
        )
        print("✓ All scrapers imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_scraper_initialization():
    """Test if scrapers can be initialized"""
    print("\n" + "=" * 70)
    print("TESTING SCRAPER INITIALIZATION")
    print("=" * 70)

    try:
        from scrapers import MRTScraper, HospitalsScraper, SchoolsScraper, URARealestateScraper

        scrapers = {
            'MRTScraper': MRTScraper(),
            'HospitalsScraper': HospitalsScraper(),
            'SchoolsScraper': SchoolsScraper(),
            'URARealestateScraper': URARealestateScraper(),
        }

        for name, scraper in scrapers.items():
            print(f"✓ {name} initialized successfully")

        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False

def test_data_structures():
    """Test if scrapers have correct data structures"""
    print("\n" + "=" * 70)
    print("TESTING DATA STRUCTURES")
    print("=" * 70)

    try:
        from scrapers import MRTScraper, HospitalsScraper, SchoolsScraper, URARealestateScraper

        # Test MRTScraper
        mrt = MRTScraper()
        assert hasattr(mrt, 'stations'), "MRTScraper missing 'stations' attribute"
        assert hasattr(mrt, 'to_dataframe'), "MRTScraper missing 'to_dataframe' method"
        print("✓ MRTScraper has correct data structure")

        # Test HospitalsScraper
        hospitals = HospitalsScraper()
        assert hasattr(hospitals, 'hospitals'), "HospitalsScraper missing 'hospitals' attribute"
        assert hasattr(hospitals, 'to_dataframe'), "HospitalsScraper missing 'to_dataframe' method"
        print("✓ HospitalsScraper has correct data structure")

        # Test SchoolsScraper
        schools = SchoolsScraper()
        assert hasattr(schools, 'schools'), "SchoolsScraper missing 'schools' attribute"
        assert hasattr(schools, 'to_dataframe'), "SchoolsScraper missing 'to_dataframe' method"
        print("✓ SchoolsScraper has correct data structure")

        # Test URARealestateScraper
        ura = URARealestateScraper()
        assert hasattr(ura, 'property_data'), "URARealestateScraper missing 'property_data' attribute"
        assert hasattr(ura, 'to_dataframe'), "URARealestateScraper missing 'to_dataframe' method"
        print("✓ URARealestateScraper has correct data structure")

        return True
    except AssertionError as e:
        print(f"✗ Data structure error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def print_summary():
    """Print summary of all scrapers"""
    print("\n" + "=" * 70)
    print("SCRAPER SUMMARY")
    print("=" * 70)

    scrapers_info = {
        'MRT Scraper': {
            'url': 'https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations',
            'source': 'Wikipedia',
            'fields': ['name', 'code', 'line', 'opening_year', 'latitude', 'longitude'],
            'output': 'data/raw/mrt_stations.csv'
        },
        'Hospitals Scraper': {
            'url': 'https://en.wikipedia.org/wiki/List_of_hospitals_in_Singapore',
            'source': 'Wikipedia',
            'fields': ['name', 'type', 'opened', 'district', 'ownership', 'beds', 'staff'],
            'output': 'data/raw/hospitals.csv'
        },
        'Schools Scraper': {
            'url': 'https://www.moe.gov.sg/schoolfinder',
            'source': 'MOE SchoolFinder',
            'fields': ['name', 'type', 'address', 'contact', 'principal', 'url'],
            'output': 'data/raw/schools.csv'
        },
        'URA Real Estate Scraper': {
            'url': 'https://www.ura.gov.sg/Corporate/Property/Property-Data',
            'source': 'URA',
            'fields': ['property_type', 'location', 'price', 'rental', 'supply', 'vacancy', 'stock', 'pipeline_supply', 'year'],
            'output': 'data/raw/ura_realestate.csv'
        }
    }

    for scraper_name, info in scrapers_info.items():
        print(f"\n{scraper_name}:")
        print(f"  Source: {info['source']}")
        print(f"  URL: {info['url']}")
        print(f"  Fields: {', '.join(info['fields'])}")
        print(f"  Output: {info['output']}")

def main():
    """Run all tests"""
    print("\n" + "█" * 70)
    print("SINGAPORE DATA ANALYTICS PROJECT - SCRAPER TEST SUITE")
    print("█" * 70)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Initialization", test_scraper_initialization()))
    results.append(("Data Structures", test_data_structures()))

    # Print summary
    print_summary()

    # Print test results
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    all_passed = True
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nYou can now run the scrapers with:")
        print("  python main.py")
        print("\nOr run individual scrapers:")
        print("  python scrapers/mrt_scraper.py")
        print("  python scrapers/hospitals_scraper.py")
        print("  python scrapers/schools_scraper.py")
        print("  python scrapers/ura_realestate_scraper.py")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please check the errors above and fix any issues.")

    print("=" * 70 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
