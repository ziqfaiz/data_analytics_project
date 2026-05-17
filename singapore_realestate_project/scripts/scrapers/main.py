import logging
from pathlib import Path
from scripts.scrapers import MRTScraper, HospitalsScraper, SchoolsScraper, URARealestateScraper

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
    """Scrape Singapore schools data from MOE SchoolFinder

    Scrapes all supported school types: preschool, primary, secondary, jc.
    All types share the same RSC Wire Protocol structure on the MOE site.
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "schools.csv"

    if output_file.exists() and output_file.stat().st_size > 100:
        print(f"✓ Schools data already exists at {output_file}")
        return
    else:
        print("Starting schools data scrape (preschool)...")
        scraper = SchoolsScraper(headless=True)
        url = "https://www.moe.gov.sg/schoolfinder"

        df = scraper.scrape(url, school_types=["preschool", "primary", "secondary", "jc"])
        print(f"\n✓ Scraped {len(df)} schools")
        print("\nFirst few schools:")
        print(df.head(10))
        print("\nColumns:", list(df.columns))

        # Save to CSV
        scraper.save_to_csv(str(output_file))
        print(f"✓ Data saved to {output_file}")

def scrape_ura_realestate_data(
    districts=None,
    property_type_ids=None,
    force=False,
):
    """
    Scrape residential transaction data from URA Property Market Information.

    Strategy: loop through 28 postal districts × 4 property types,
    POST directly to the URA PMI CSV download endpoint, parse the CSV response,
    and accumulate all transaction records.

    Args:
        districts         : List of 0-based indices into POSTAL_DISTRICTS
                            (None = all 28). Use [0, 1] for a quick test
                            (D01 + D02).
        property_type_ids : List of type strings "1"–"4" (None = all 4).
                            1 = Landed Properties (Non-Strata)
                            2 = Strata Landed
                            3 = Apartments & Condominiums
                            4 = Executive Condominiums
        force             : Re-scrape even if output file already exists.
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "ura_pmi_transactions.csv"

    if output_file.exists() and not force:
        print(f"✓ URA PMI transaction data already exists at {output_file}")
        print("  Pass force=True (or delete the file) to re-scrape.")
        return

    print("Starting URA PMI residential transaction scrape...")
    print("  Looping: 28 postal districts × 4 property types")
    print("  Sale date: Apr 2021 – Apr 2026 (default)")
    print("  Sale type: All (New Sale + Sub Sale + Resale)")
    print()

    scraper = URARealestateScraper(headless=True)

    df = scraper.scrape(
        districts=districts,
        property_type_ids=property_type_ids,
    )

    if df is not None and not df.empty:
        print(f"\n✓ Scraped {len(df)} transaction records")
        print(f"\nProperty type breakdown:")
        print(df["property_type"].value_counts().to_string())
        print(f"\nPostal districts covered: {sorted(df['postal_district'].unique())}")
        print(f"\nSale date range: {df['sale_date'].min()} → {df['sale_date'].max()}")
        print(f"\nFirst few records:")
        print(df.head(5).to_string())

        df.to_csv(output_file, index=False)
        print(f"\n✓ Data saved to {output_file}")
    else:
        print("✗ No data scraped — check logs for errors")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    scrape_mrt_data()
    print()
    scrape_hospital_data()
    print()
    scrape_schools_data()
    print()
    scrape_ura_realestate_data()


