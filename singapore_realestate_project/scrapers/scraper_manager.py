"""
Scraper Manager
Orchestrates multiple scrapers and combines results
"""

import pandas as pd
import logging
from pathlib import Path
from .propertyguru_scraper import PropertyGuruScraper
from .edgeprop_scraper import EdgePropScraper
from .mrt_scraper import MRTScraper
from .schools_scraper import SchoolsScraper
from .hospitals_scraper import HospitalsScraper
from .ura_realestate_scraper import URARealestateScraper

logger = logging.getLogger(__name__)


class ScraperManager:
    """Manage and coordinate multiple property portal scrapers"""

    def __init__(self, output_dir="data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}

    def scrape_propertyguru(self, url, max_pages=5, save=True):
        """
        Scrape PropertyGuru

        Args:
            url: PropertyGuru search URL
            max_pages: Number of pages to scrape
            save: Save results to CSV

        Returns:
            DataFrame with scraped data
        """
        logger.info("Starting PropertyGuru scrape...")
        scraper = PropertyGuruScraper(headless=True)

        try:
            df = scraper.scrape(url, max_pages=max_pages)
            if df is not None and not df.empty:
                self.results['propertyguru'] = df
                if save:
                    filepath = self.output_dir / "propertyguru_listings.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {len(df)} PropertyGuru listings to {filepath}")
                return df
            else:
                logger.warning("No data scraped from PropertyGuru")
                return None
        except Exception as e:
            logger.error(f"PropertyGuru scraping failed: {e}")
            return None

    def scrape_edgeprop(self, url, max_pages=5, save=True):
        """
        Scrape EdgeProp

        Args:
            url: EdgeProp search URL
            max_pages: Number of pages to scrape
            save: Save results to CSV

        Returns:
            DataFrame with scraped data
        """
        logger.info("Starting EdgeProp scrape...")
        scraper = EdgePropScraper(headless=True)

        try:
            df = scraper.scrape(url, max_pages=max_pages)
            if df is not None and not df.empty:
                self.results['edgeprop'] = df
                if save:
                    filepath = self.output_dir / "edgeprop_listings.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {len(df)} EdgeProp listings to {filepath}")
                return df
            else:
                logger.warning("No data scraped from EdgeProp")
                return None
        except Exception as e:
            logger.error(f"EdgeProp scraping failed: {e}")
            return None

    def scrape_mrt_stations(self, url, save=True):
        """
        Scrape Singapore MRT stations from Wikipedia

        Args:
            url: Wikipedia MRT stations URL
            save: Save results to CSV

        Returns:
            DataFrame with MRT station data
        """
        logger.info("Starting MRT stations scrape...")
        scraper = MRTScraper(headless=True)

        try:
            df = scraper.scrape(url)
            if df is not None and not df.empty:
                self.results['mrt_stations'] = df
                if save:
                    filepath = self.output_dir / "mrt_stations.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {len(df)} MRT stations to {filepath}")
                return df
            else:
                logger.warning("No data scraped from MRT")
                return None
        except Exception as e:
            logger.error(f"MRT scraping failed: {e}")
            return None

    def scrape_schools(self, url, school_types=None, save=True):
        """
        Scrape Singapore schools from MOE

        Args:
            url: MOE SchoolFinder URL
            school_types: List of school types to scrape
            save: Save results to CSV

        Returns:
            DataFrame with school data
        """
        logger.info("Starting schools scrape...")
        scraper = SchoolsScraper(headless=True)

        try:
            df = scraper.scrape(url, school_types=school_types)
            if df is not None and not df.empty:
                self.results['schools'] = df
                if save:
                    filepath = self.output_dir / "schools.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {len(df)} schools to {filepath}")
                return df
            else:
                logger.warning("No data scraped from schools")
                return None
        except Exception as e:
            logger.error(f"Schools scraping failed: {e}")
            return None

    def scrape_hospitals(self, url, save=True):
        """
        Scrape Singapore hospitals from SGDI

        Args:
            url: SGDI hospitals URL
            save: Save results to CSV

        Returns:
            DataFrame with hospital data
        """
        logger.info("Starting hospitals scrape...")
        scraper = HospitalsScraper(headless=True)

        try:
            df = scraper.scrape(url)
            if df is not None and not df.empty:
                self.results['hospitals'] = df
                if save:
                    filepath = self.output_dir / "hospitals.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {len(df)} hospitals to {filepath}")
                return df
            else:
                logger.warning("No data scraped from hospitals")
                return None
        except Exception as e:
            logger.error(f"Hospitals scraping failed: {e}")
            return None

    def scrape_ura_realestate(self, url, property_types=None, save=True):
        """
        Scrape Singapore real estate data from URA

        Args:
            url: URA property data URL
            property_types: List of property types ('residential', 'commercial')
            save: Save results to CSV

        Returns:
            DataFrame with property data
        """
        logger.info("Starting URA real estate scrape...")
        scraper = URARealestateScraper(headless=True)

        try:
            df = scraper.scrape(url, property_types=property_types)
            if df is not None and not df.empty:
                self.results['ura_realestate'] = df
                if save:
                    filepath = self.output_dir / "ura_realestate.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {len(df)} property records to {filepath}")
                return df
            else:
                logger.warning("No data scraped from URA")
                return None
        except Exception as e:
            logger.error(f"URA scraping failed: {e}")
            return None

    def combine_results(self, save=True):
        """
        Combine results from all scrapers

        Args:
            save: Save combined results to CSV

        Returns:
            Combined DataFrame
        """
        if not self.results:
            logger.warning("No results to combine")
            return None

        logger.info(f"Combining results from {len(self.results)} sources...")

        dfs = list(self.results.values())
        combined_df = pd.concat(dfs, ignore_index=True)

        logger.info(f"Combined {len(combined_df)} total listings from all sources")

        if save:
            filepath = self.output_dir / "private_properties_combined.csv"
            combined_df.to_csv(filepath, index=False)
            logger.info(f"Saved combined data to {filepath}")

        return combined_df

    def get_statistics(self):
        """Get scraping statistics"""
        stats = {}
        for source, df in self.results.items():
            stats[source] = {
                'count': len(df),
                'columns': len(df.columns),
                'price_avg': df['price'].mean() if 'price' in df.columns else None,
                'price_min': df['price'].min() if 'price' in df.columns else None,
                'price_max': df['price'].max() if 'price' in df.columns else None,
            }
        return stats

    def print_statistics(self):
        """Print scraping statistics"""
        stats = self.get_statistics()
        print("\n" + "=" * 60)
        print("SCRAPING STATISTICS")
        print("=" * 60)

        for source, data in stats.items():
            print(f"\n{source.upper()}:")
            print(f"  Properties scraped: {data['count']}")
            print(f"  Columns: {data['columns']}")
            if data['price_avg']:
                print(f"  Price range: ${data['price_min']:,.0f} - ${data['price_max']:,.0f}")
                print(f"  Average price: ${data['price_avg']:,.0f}")

        total = sum([data['count'] for data in stats.values()])
        print(f"\nTotal properties: {total}")
        print("=" * 60)


def main():
    """Example usage"""
    manager = ScraperManager()

    print("""
    ScraperManager ready to use!

    === PROPERTY SCRAPERS ===
    Scrape PropertyGuru and EdgeProp for private residential properties.

    Usage example:
    ---------------
    manager = ScraperManager()

    # Scrape PropertyGuru
    pg_url = "https://www.propertyguru.com.sg/property-for-sale?market=residential"
    pg_df = manager.scrape_propertyguru(pg_url, max_pages=5)

    # Scrape EdgeProp
    ep_url = "https://www.edgeprop.sg/property/search/residential"
    ep_df = manager.scrape_edgeprop(ep_url, max_pages=5)

    # Scrape URA Real Estate Data
    ura_url = "https://www.ura.gov.sg/Corporate/Property/Property-Data"
    ura_df = manager.scrape_ura_realestate(ura_url, property_types=['residential', 'commercial'])

    # Combine property data and print stats
    combined = manager.combine_results()
    manager.print_statistics()


    === LOCATION-BASED SCRAPERS ===
    Scrape transport, education, and healthcare infrastructure data.

    # Scrape MRT Stations
    mrt_url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"
    mrt_df = manager.scrape_mrt_stations(mrt_url)

    # Scrape Schools
    schools_url = "https://www.moe.gov.sg/schoolfinder"
    schools_df = manager.scrape_schools(schools_url, school_types=['primary', 'secondary'])

    # Scrape Hospitals
    hospitals_url = "https://www.sgdi.gov.sg/other-organisations/hospitals"
    hospitals_df = manager.scrape_hospitals(hospitals_url)


    === INTEGRATED EXAMPLE ===
    from scrapers import ScraperManager

    manager = ScraperManager(output_dir="data/raw")

    # Scrape all data sources
    mrt_df = manager.scrape_mrt_stations("https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations")
    schools_df = manager.scrape_schools("https://www.moe.gov.sg/schoolfinder")
    hospitals_df = manager.scrape_hospitals("https://www.sgdi.gov.sg/other-organisations/hospitals")
    ura_df = manager.scrape_ura_realestate("https://www.ura.gov.sg/Corporate/Property/Property-Data")

    print(f"Scraped {len(mrt_df)} MRT stations")
    print(f"Scraped {len(schools_df)} schools")
    print(f"Scraped {len(hospitals_df)} hospitals")
    print(f"Scraped {len(ura_df)} property records")
    """)


if __name__ == "__main__":
    main()
