import logging
from pathlib import Path
from scrapers import MRTScraper, HospitalsScraper, SchoolsScraper, URARealestateScraper

def scrape_mrt_data():
    """Scrape Singapore MRT station data from Wikipedia"""
    # Create output directory if it doesn't exist
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "mrt_stations.csv"

    # Only scrape if file doesn't already exist
    if output_file.exists():
        print(f"✓ MRT data already exists at {output_file}")
        return
    else:
        print("Starting MRT data scrape...")
        scraper = MRTScraper(headless=True)
        url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"

        df = scraper.scrape(url)
        print(f"\n✓ Scraped {len(df)} MRT stations")
        print("\nFirst few stations:")
        print(df.head(10))

        # Save to CSV
        scraper.save_to_csv(str(output_file))
        print(f"✓ Data saved to {output_file}")

def scrape_hospital_data():
    """Scrape Singapore hospital data from Wikipedia"""
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "hospitals.csv"

    if output_file.exists():
        print(f"✓ Hospital data already exists at {output_file}")
        return
    else:
        print("Starting hospital data scrape...")
        scraper = HospitalsScraper(headless=True)
        url = "https://en.wikipedia.org/wiki/List_of_hospitals_in_Singapore"

        df = scraper.scrape(url)
        print(f"\n✓ Scraped {len(df)} hospitals")
        print("\nFirst few hospitals:")
        print(df.head(10))

        # Save to CSV
        scraper.save_to_csv(str(output_file))
        print(f"✓ Data saved to {output_file}")

def scrape_schools_data():
    """Scrape Singapore schools data from MOE SchoolFinder"""
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "schools.csv"

    if output_file.exists():
        print(f"✓ Schools data already exists at {output_file}")
        return
    else:
        print("Starting schools data scrape...")
        scraper = SchoolsScraper(headless=True)
        url = "https://www.moe.gov.sg/schoolfinder"

        # Scrape all school types
        df = scraper.scrape(url, school_types=['preschool', 'primary', 'secondary', 'jc', 'college'])
        print(f"\n✓ Scraped {len(df)} schools")
        print("\nFirst few schools:")
        print(df.head(10))

        # Save to CSV
        scraper.save_to_csv(str(output_file))
        print(f"✓ Data saved to {output_file}")

def scrape_ura_realestate_data():
    """Scrape Singapore real estate data from URA"""
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "ura_realestate.csv"

    if output_file.exists():
        print(f"✓ URA real estate data already exists at {output_file}")
        return
    else:
        print("Starting URA real estate data scrape...")
        scraper = URARealestateScraper(headless=True)
        url = "https://www.ura.gov.sg/Corporate/Property/Property-Data"

        df = scraper.scrape(url, property_types=['residential', 'commercial'])
        print(f"\n✓ Scraped {len(df)} property records")
        print("\nFirst few records:")
        print(df.head(10))

        # Save to CSV
        scraper.save_to_csv(str(output_file))
        print(f"✓ Data saved to {output_file}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)


    scrape_mrt_data()
    print()
    scrape_hospital_data()
    #print()
    scrape_schools_data()
    #print()
    scrape_ura_realestate_data()


