"""
Data Collection Script
Collect real estate data, school/hospital/MRT locations from various sources
"""

import os
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pathlib import Path
from config import RAW_DATA_DIR, DATA_SOURCES, GOOGLE_MAPS_API_KEY
import googlemaps

class DataCollector:
    """Collect data from various sources"""

    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
        self.gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY) if GOOGLE_MAPS_API_KEY else None

    def download_hdb_data(self):
        """
        Download HDB resale data from data.gov.sg
        Note: Actual implementation depends on data.gov.sg API structure
        """
        print("Downloading HDB resale data...")
        print("TODO: Implement HDB data download from data.gov.sg")
        print("Source: https://data.gov.sg/datasets")

    def download_moe_schools(self):
        """
        Download school locations from MOE data portal
        """
        print("Downloading school locations...")
        print("TODO: Implement school data download from data.gov.sg")
        print("Source: Ministry of Education")

    def download_moh_hospitals(self):
        """
        Download hospital locations from MOH data
        """
        print("Downloading hospital locations...")
        print("TODO: Implement hospital data download")
        print("Source: Ministry of Health")

    def scrape_private_properties(self, url, headless=True):
        """
        Scrape private property data using Selenium

        Args:
            url: Website URL to scrape
            headless: Run browser in headless mode
        """
        print(f"Scraping property data from {url}...")

        # Chrome options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            # Wait for page to load
            time.sleep(2)

            # TODO: Implement scraping logic
            # Example:
            # properties = driver.find_elements(By.CLASS_NAME, "property-card")
            # for prop in properties:
            #     # Extract data
            #     pass

            print("TODO: Implement Selenium scraping logic")

        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            if driver:
                driver.quit()

    def get_location_coordinates(self, address, location_type="address"):
        """
        Get coordinates for an address using Google Maps API

        Args:
            address: Address string
            location_type: Type of location (address, school, hospital, mrt)

        Returns:
            dict with latitude, longitude
        """
        if not self.gmaps:
            print("Google Maps API key not set!")
            return None

        try:
            geocode_result = self.gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'address': geocode_result[0]['formatted_address']
                }
        except Exception as e:
            print(f"Error geocoding {address}: {e}")

        return None

    def get_nearby_schools(self, latitude, longitude, radius=2000):
        """
        Find schools near a location using Google Places API

        Args:
            latitude, longitude: Location coordinates
            radius: Search radius in meters

        Returns:
            list of nearby schools
        """
        if not self.gmaps:
            print("Google Maps API key not set!")
            return []

        try:
            places_result = self.gmaps.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                type='school'
            )
            return places_result.get('results', [])
        except Exception as e:
            print(f"Error getting nearby places: {e}")
            return []

    def get_mrt_stations(self):
        """
        Get MRT station locations
        Can use predefined list or scrape from OpenStreetMap/official sources
        """
        print("Fetching MRT station data...")
        print("TODO: Implement MRT station data collection")

        # Predefined MRT stations can be used as fallback
        mrt_stations = [
            {"name": "Ang Mo Kio", "latitude": 1.3699, "longitude": 103.8453},
            {"name": "Bishan", "latitude": 1.3514, "longitude": 103.8471},
            # Add more stations...
        ]

        return mrt_stations

    def save_raw_data(self, data, filename):
        """Save raw data to CSV"""
        filepath = self.raw_data_dir / filename
        data.to_csv(filepath, index=False)
        print(f"Saved to {filepath}")

    def run_collection(self):
        """Run all data collection tasks"""
        print("=" * 60)
        print("STARTING DATA COLLECTION")
        print("=" * 60)

        self.download_hdb_data()
        self.download_moe_schools()
        self.download_moh_hospitals()
        self.get_mrt_stations()

        # Example: Scrape PropertyGuru
        # self.scrape_private_properties("https://www.propertyguru.com.sg/")

        print("=" * 60)
        print("DATA COLLECTION COMPLETE")
        print("=" * 60)

def main():
    collector = DataCollector()
    collector.run_collection()

if __name__ == "__main__":
    main()
