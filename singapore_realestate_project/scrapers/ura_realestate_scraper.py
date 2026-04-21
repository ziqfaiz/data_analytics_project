"""
Singapore Real Estate Data Scraper (URA)

Scrapes real estate property data from URA
https://www.ura.gov.sg/Corporate/Property/Property-Data
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging
import time
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class URARealestateScraper(BaseScraper):
    """Scraper for Singapore real estate data from URA"""

    def __init__(self, headless=True, implicit_wait=10):
        """Initialize URA realestate scraper"""
        super().__init__(headless=headless, implicit_wait=implicit_wait)
        self.properties = []
        self.property_data = []

    def scrape(self, url, property_types=None):
        """
        Scrape real estate data from URA

        Args:
            url: URA property data URL
            property_types: List of property types to scrape
                           ['residential', 'commercial']
                           If None, scrapes all types

        Returns:
            pd.DataFrame: DataFrame containing property data
        """
        if property_types is None:
            property_types = ['residential', 'commercial']

        self.setup_driver()
        try:
            self.get_page(url)
            self._accept_cookies()

            for prop_type in property_types:
                logger.info(f"Scraping {prop_type} properties...")
                self._scrape_property_type(prop_type)

            return self.to_dataframe()
        finally:
            self.close_driver()

    def _accept_cookies(self):
        """Accept cookies if present"""
        try:
            cookie_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'Accept')] | //button[contains(text(), 'agree')]"
            )
            if cookie_buttons:
                cookie_buttons[0].click()
                logger.info("Cookies accepted")
                time.sleep(1)
        except Exception as e:
            logger.debug(f"No cookie banner found: {e}")

    def _scrape_property_type(self, property_type):
        """
        Scrape properties of a specific type

        Args:
            property_type: Type of property ('residential', 'commercial')
        """
        try:
            # Select property type
            self._select_property_type(property_type)
            time.sleep(2)

            # Try to find and download data tables
            self._extract_property_data(property_type)

        except Exception as e:
            logger.warning(f"Error scraping {property_type} properties: {e}")

    def _select_property_type(self, property_type):
        """Select property type from filters"""
        try:
            # Try to find and click on property type selector
            selectors = [
                f"//button[contains(., '{property_type.capitalize()}')]",
                f"//a[contains(., '{property_type.capitalize()}')]",
                f"//label[contains(., '{property_type.capitalize()}')]",
            ]

            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    element.click()
                    logger.info(f"Selected {property_type}")
                    return
                except:
                    continue

            logger.warning(f"Could not select {property_type}")
        except Exception as e:
            logger.warning(f"Error selecting property type: {e}")

    def _extract_property_data(self, property_type):
        """Extract property data from tables on the page"""
        try:
            # Scroll to load data
            self.scroll_to_bottom()
            time.sleep(2)

            # Find data tables
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            logger.info(f"Found {len(tables)} tables")

            for table_idx, table in enumerate(tables):
                try:
                    self._extract_from_data_table(table, property_type)
                except Exception as e:
                    logger.debug(f"Error extracting from table {table_idx}: {e}")

        except Exception as e:
            logger.warning(f"Error extracting property data: {e}")

    def _extract_from_data_table(self, table, property_type):
        """Extract data from a specific table"""
        try:
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            logger.info(f"Found {len(rows)} rows in table")

            # Get headers
            headers = []
            try:
                header_cells = table.find_elements(By.CSS_SELECTOR, "thead th")
                headers = [cell.text.strip() for cell in header_cells]
            except:
                header_cells = table.find_elements(By.CSS_SELECTOR, "tbody tr:first-child td")
                headers = [cell.text.strip() for cell in header_cells]
                rows = rows[1:]  # Skip header row

            logger.debug(f"Table headers: {headers}")

            # Process data rows
            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    if len(cells) > 0:
                        row_data = self._parse_property_row(cells, headers, property_type)
                        if row_data.get('location') or row_data.get('property_type'):
                            self.property_data.append(row_data)
                            logger.debug(f"Extracted: {row_data}")
                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")

        except Exception as e:
            logger.warning(f"Error extracting from table: {e}")

    def _parse_property_row(self, cells, headers, property_type):
        """Parse a row of property data"""
        row_data = {
            'property_type': property_type,
            'location': '',
            'price': '',
            'rental': '',
            'supply': '',
            'vacancy': '',
            'stock': '',
            'pipeline_supply': '',
            'year': ''
        }

        try:
            cell_texts = [cell.text.strip() for cell in cells]

            # Map cells to data based on headers
            for idx, header in enumerate(headers):
                if idx >= len(cell_texts):
                    break

                value = cell_texts[idx]
                header_lower = header.lower()

                # Categorize the data based on header
                if any(x in header_lower for x in ['location', 'district', 'area', 'region']):
                    row_data['location'] = value
                elif any(x in header_lower for x in ['price', 'median price', 'average price']):
                    row_data['price'] = value
                elif any(x in header_lower for x in ['rental', 'rent']):
                    row_data['rental'] = value
                elif 'supply' in header_lower and 'pipeline' not in header_lower:
                    row_data['supply'] = value
                elif 'pipeline' in header_lower:
                    row_data['pipeline_supply'] = value
                elif 'vacancy' in header_lower:
                    row_data['vacancy'] = value
                elif 'stock' in header_lower:
                    row_data['stock'] = value
                elif any(x in header_lower for x in ['year', 'period', 'quarter']):
                    row_data['year'] = value
                elif not row_data['location']:  # Use first column as location if not assigned
                    row_data['location'] = value

        except Exception as e:
            logger.debug(f"Error parsing property row: {e}")

        return row_data

    def to_dataframe(self):
        """Convert scraped properties to DataFrame"""
        if self.property_data:
            df = pd.DataFrame(self.property_data)
        else:
            df = pd.DataFrame(self.properties)
        logger.info(f"Converted {len(df)} properties to DataFrame")
        return df


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = URARealestateScraper(headless=True)
    url = "https://www.ura.gov.sg/Corporate/Property/Property-Data"

    df = scraper.scrape(url, property_types=['residential', 'commercial'])
    print(f"\nScraped {len(df)} property records")
    print("\nFirst few records:")
    print(df.head(10))

    # Save to CSV
    scraper.save_to_csv("data/raw/ura_realestate.csv")
