"""
Singapore MRT Stations Scraper

Scrapes MRT station information from Wikipedia
https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations
"""

from selenium.webdriver.common.by import By
import pandas as pd
import logging
import re
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

    def to_dataframe(self):
        """Convert scraped stations to DataFrame"""
        df = pd.DataFrame(self.stations)
        logger.info(f"Converted {len(df)} stations to DataFrame")
        return df

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

            # Skip header rows (first 2 rows are headers)
            data_rows = rows[2:] if len(rows) > 2 else rows

            for row in data_rows:
                try:
                    # Get ALL cells including th (row headers) and td
                    all_cells = row.find_elements(By.CSS_SELECTOR, "th, td")

                    if len(all_cells) < 4:
                        continue

                    cells = all_cells

                    station_data = self._parse_row(cells)

                    # Only add if name and code exist
                    if station_data["name"] and station_data["code"]:
                        self.stations.append(station_data)
                        logger.debug(
                            f"Extracted: {station_data['name']} "
                            f"({station_data['code']}) - {station_data['line']}"
                        )

                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error processing table {table_idx}: {e}")

    def _parse_row(self, cells):
        """
        Parse a table row to extract station information.

        Wikipedia table structure (known positions):
        [0] English name (th)
        [1] Chinese name (td)
        [2] Tamil name (td)
        [3] Station code (td) - format: "NS10"
        [4] Line (td) - format: "North–South Line"
        [5] Opened date (td) - format: "10 February 1996"
        [6+] Connections and references

        Args:
            cells: List of all cells (th + td elements)

        Returns:
            dict: Dictionary with station data
        """
        station_data = {
            "name": "",
            "code": "",
            "line": "",
            "opening_year": "",
            "latitude": "",
            "longitude": "",
        }

        try:
            if len(cells) < 6:
                return station_data

            cell_texts = [cell.text.strip() for cell in cells]

            # Position 0: English station name (in <th>)
            station_data["name"] = cell_texts[0]

            # Position 3: Station code (e.g., "NS10", "EW1")
            code_text = cell_texts[3]
            code = self._extract_code_from_text(code_text)
            if code:
                station_data["code"] = code

            # Position 4: Line information (e.g., "North–South Line")
            line_text = cell_texts[4]
            line = self._extract_line_code(line_text)
            if line:
                station_data["line"] = line

            # Position 5: Opening date (e.g., "10 February 1996")
            date_text = cell_texts[5]
            year = self._extract_year(date_text)
            if year:
                station_data["opening_year"] = year

        except Exception as e:
            logger.debug(f"Error parsing row content: {e}")

        return station_data

    @staticmethod
    def _extract_code_from_text(text):
        """Extract station code from text (handles HTML markup)"""
        # Remove extra whitespace and search for pattern like NS10, EW1, etc.
        text = text.replace("\n", " ").strip()
        match = re.search(r"([A-Z]{2,3}\d+)", text)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_line_code(line_text):
        """Extract line code from line name"""
        line_mapping = {
            "North-South": "NS",
            "North–South": "NS",  # en-dash version
            "East-West": "EW",
            "East–West": "EW",
            "North-East": "NE",
            "North–East": "NE",
            "Circle": "CC",
            "Downtown": "DT",
            "Thomson": "TE",
            "Jurong Region": "JR",
        }

        for line_name, code in line_mapping.items():
            if line_name.lower() in line_text.lower():
                return code

        return ""


    @staticmethod
    def _extract_year(text):
        """Extract opening year from text"""
        match = re.search(r"\b(19|20)\d{2}\b", text)
        return match.group(0) if match else ""


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
