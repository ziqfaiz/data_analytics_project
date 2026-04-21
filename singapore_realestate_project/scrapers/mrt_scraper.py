"""
Singapore MRT Stations Scraper

Scrapes MRT station information from Wikipedia
https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations
"""

from selenium.webdriver.common.by import By
import pandas as pd
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MRTScraper(BaseScraper):
    """Scraper for Singapore MRT station data from Wikipedia"""

    def __init__(self, headless=True, implicit_wait=10):
        """Initialize MRT scraper"""
        super().__init__(headless=headless, implicit_wait=implicit_wait)
        self.stations = []

    def scrape(self, url):
        """
        Scrape MRT stations from Wikipedia

        Args:
            url: Wikipedia URL for MRT stations list

        Returns:
            pd.DataFrame: DataFrame containing MRT station data
        """
        self.setup_driver()
        try:
            self.get_page(url)
            self._extract_stations_from_tables()
            return self.to_dataframe()
        finally:
            self.close_driver()

    def _extract_stations_from_tables(self):
        """Extract station data from Wikipedia tables"""
        try:
            # Find all tables on the page
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table.wikitable")
            logger.info(f"Found {len(tables)} tables on the page")

            for table_idx, table in enumerate(tables):
                logger.info(f"Processing table {table_idx + 1}")
                self._extract_from_table(table, table_idx)

            logger.info(f"Total stations extracted: {len(self.stations)}")
        except Exception as e:
            logger.error(f"Error extracting stations from tables: {e}")

    def _extract_from_table(self, table, table_idx):
        """
        Extract station data from a single table

        Args:
            table: WebElement representing the table
            table_idx: Index of the table being processed
        """
        try:
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

            # Skip header row
            data_rows = rows[1:] if len(rows) > 1 else rows

            for row in data_rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")

                    if len(cells) < 3:
                        continue

                    station_data = self._parse_row(cells)

                    if station_data['name']:  # Only add if name exists
                        self.stations.append(station_data)
                        logger.debug(f"Extracted: {station_data['name']} ({station_data['line']})")

                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error processing table {table_idx}: {e}")

    def _parse_row(self, cells):
        """
        Parse a table row to extract station information

        Args:
            cells: List of table cells (td elements)

        Returns:
            dict: Dictionary with station data
        """
        station_data = {
            'name': '',
            'code': '',
            'line': '',
            'opening_year': '',
            'latitude': '',
            'longitude': ''
        }

        try:
            # Column order may vary, try to identify columns by content

            # First cell usually contains station name (or code + name)
            name_text = cells[0].text.strip()

            # Try to extract station code if present (usually in format like "NS1")
            code = ''
            if len(name_text.split()) > 0:
                # Check if first part looks like a code (e.g., "NS1", "EW1")
                potential_code = name_text.split()[0]
                if len(potential_code) <= 4 and any(c.isdigit() for c in potential_code):
                    code = potential_code
                    station_data['code'] = code

            station_data['name'] = name_text

            # Second cell usually contains line information
            if len(cells) > 1:
                line_text = cells[1].text.strip()
                # Extract line code (e.g., "North-South Line" -> "NS")
                line_code = self._extract_line_code(line_text)
                station_data['line'] = line_code or line_text

            # Look for year information in remaining cells
            if len(cells) > 2:
                year_text = cells[2].text.strip()
                year = self._extract_year(year_text)
                if year:
                    station_data['opening_year'] = year

            # Try to extract coordinates from later cells
            for i in range(3, len(cells)):
                cell_text = cells[i].text.strip()
                coords = self._extract_coordinates(cell_text)
                if coords['latitude'] and coords['longitude']:
                    station_data['latitude'] = coords['latitude']
                    station_data['longitude'] = coords['longitude']
                    break

        except Exception as e:
            logger.debug(f"Error parsing row content: {e}")

        return station_data

    @staticmethod
    def _extract_line_code(line_text):
        """Extract line code from line name"""
        line_mapping = {
            'North-South': 'NS',
            'East-West': 'EW',
            'North-East': 'NE',
            'Circle': 'CC',
            'Downtown': 'DT',
            'Thomson': 'TE',
        }

        for line_name, code in line_mapping.items():
            if line_name.lower() in line_text.lower():
                return code

        return None

    @staticmethod
    def _extract_year(text):
        """Extract opening year from text"""
        import re
        match = re.search(r'\b(19|20)\d{2}\b', text)
        return match.group(0) if match else ''

    @staticmethod
    def _extract_coordinates(text):
        """Extract latitude and longitude from text"""
        import re
        coords = {'latitude': '', 'longitude': ''}

        # Pattern for coordinates like "1.3521°N 103.8198°E"
        pattern = r'(\d+\.\d+)°[NS]\s+(\d+\.\d+)°[EW]'
        match = re.search(pattern, text)

        if match:
            coords['latitude'] = match.group(1)
            coords['longitude'] = match.group(2)

        return coords


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = MRTScraper(headless=True)
    url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"

    df = scraper.scrape(url)
    print(f"\nScraped {len(df)} MRT stations")
    print("\nFirst few stations:")
    print(df.head(10))

    # Save to CSV
    scraper.save_to_csv("data/raw/mrt_stations.csv")
