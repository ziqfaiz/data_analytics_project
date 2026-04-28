"""
Singapore Hospitals Scraper

Scrapes hospital information from Wikipedia
https://en.wikipedia.org/wiki/List_of_hospitals_in_Singapore
"""

from selenium.webdriver.common.by import By
import pandas as pd
import logging
import re
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HospitalsScraper(BaseScraper):
    """Scraper for Singapore hospital data from Wikipedia"""

    def __init__(self, headless=True, implicit_wait=10):
        """Initialize hospitals scraper"""
        super().__init__(headless=headless, implicit_wait=implicit_wait)
        self.hospitals = []

    def scrape(self, url, hospital_types=None):
        """
        Scrape hospitals from Wikipedia

        Args:
            url: Wikipedia hospitals URL
            hospital_types: List of hospital types to scrape
                           ['acute', 'community', 'psychiatric']
                           If None, scrapes all types

        Returns:
            pd.DataFrame: DataFrame containing hospital data
        """
        if hospital_types is None:
            hospital_types = ["acute", "community", "psychiatric"]

        self.setup_driver()
        try:
            self.get_page(url)
            self._scrape_hospital_tables(hospital_types)
            logger.info(f"Total hospitals extracted: {len(self.hospitals)}")
            return self.to_dataframe()
        finally:
            self.close_driver()

    def _scrape_hospital_tables(self, hospital_types):
        """
        Scrape all hospital tables and determine their types

        Args:
            hospital_types: List of hospital types to extract
        """
        try:
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table.wikitable.sortable")
            logger.info(f"Found {len(tables)} wikitable sortable tables on the page")

            for table_idx, table in enumerate(tables):
                try:
                    # Determine hospital type by checking preceding heading
                    hospital_type = self._determine_hospital_type(table)

                    if hospital_type and hospital_type.lower() in [t.lower() for t in hospital_types]:
                        logger.info(f"Processing {hospital_type} hospitals table")
                        self._extract_from_hospital_table(table, hospital_type)
                    else:
                        logger.debug(f"Skipping table {table_idx} - type: {hospital_type}")

                except Exception as e:
                    logger.debug(f"Error processing table {table_idx}: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error finding hospital tables: {e}")

    def _determine_hospital_type(self, table):
        """
        Determine hospital type by checking the preceding h2 heading

        Args:
            table: WebElement representing the hospital table

        Returns:
            str: Hospital type ('Acute', 'Community', 'Psychiatric') or None
        """
        try:
            heading = table.find_element(By.XPATH, "preceding::h2[1]")
            heading_text = heading.text.strip()

            if "acute" in heading_text.lower():
                return "Acute"
            elif "community" in heading_text.lower():
                return "Community"
            elif "psychiatric" in heading_text.lower():
                return "Psychiatric"
            else:
                logger.debug(f"Unknown hospital type heading: {heading_text}")
                return None

        except Exception as e:
            logger.debug(f"Error determining hospital type: {e}")
            return None

    def _extract_from_hospital_table(self, table, hospital_type):
        """
        Extract hospital data from a table, handling rowspan cells

        Args:
            table: WebElement representing the hospital table
            hospital_type: Type of hospital ('Acute', 'Community', 'Psychiatric')
        """
        try:
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

            # Skip header row (first row is header with th elements)
            data_rows = rows[1:] if len(rows) > 1 else rows
            logger.info(f"Found {len(data_rows)} {hospital_type} hospital rows")

            # Track ownership values from rowspan cells
            current_ownership = None
            ownership_remaining = 0

            for row_idx, row in enumerate(data_rows):
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")

                    if len(cells) < 4:
                        continue

                    hospital_data = self._parse_hospital_row(
                        cells, hospital_type, current_ownership
                    )

                    # Check if this row introduced a new ownership (with rowspan)
                    if len(cells) > 3:
                        ownership_cell = cells[3]
                        rowspan_str = ownership_cell.get_attribute("rowspan")

                        if rowspan_str:
                            # This row has a new ownership value with rowspan
                            current_ownership = self._clean_text(
                                ownership_cell.text.strip()
                            )
                            ownership_remaining = int(rowspan_str) - 1
                        elif ownership_remaining > 0:
                            # Continue using the previous ownership
                            ownership_remaining -= 1
                        else:
                            # This cell has explicit ownership data
                            current_ownership = self._clean_text(cells[3].text.strip())

                    if hospital_data["name"]:
                        self.hospitals.append(hospital_data)
                        logger.debug(
                            f"Extracted: {hospital_data['name']} "
                            f"({hospital_data['type']}) - {hospital_data['district']}"
                        )

                except Exception as e:
                    logger.debug(f"Error parsing hospital row: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error extracting from hospital table: {e}")

    def _parse_hospital_row(self, cells, hospital_type, current_ownership):
        """
        Parse a hospital row to extract data.

        Wikipedia table structure:
        [0] Name (in <a> tag)
        [1] Opened (year)
        [2] District (in <a> tag)
        [3] Ownership (text, may have rowspan) OR be missing if ownership is from rowspan
        [4] Beds (number) - OR position 3 if ownership cell has rowspan
        [5] Staff (number, optional)

        Args:
            cells: List of table cells (td elements)
            hospital_type: Type of hospital
            current_ownership: Ownership value from rowspan (if applicable)

        Returns:
            dict: Dictionary with hospital data
        """
        hospital_data = {
            "name": "",
            "type": hospital_type,
            "opened": "",
            "district": "",
            "ownership": current_ownership or "",
            "beds": "",
            "staff": "",
        }

        try:
            if len(cells) < 4:
                return hospital_data

            # Position 0: Hospital name (in <a> tag or plain text)
            try:
                link = cells[0].find_element(By.TAG_NAME, "a")
                hospital_data["name"] = link.text.strip()
            except:
                hospital_data["name"] = cells[0].text.strip()

            # Position 1: Opened year
            hospital_data["opened"] = cells[1].text.strip()

            # Position 2: District (may be in <a> tag)
            try:
                link = cells[2].find_element(By.TAG_NAME, "a")
                hospital_data["district"] = link.text.strip()
            except:
                hospital_data["district"] = cells[2].text.strip()

            # Position 3+: Determine if it's ownership or beds
            # Check if cells[3] has rowspan - if it does, it's ownership
            # If it doesn't have rowspan but we're on a rowspan continuation, it's beds
            if len(cells) > 3:
                cell_3_rowspan = cells[3].get_attribute("rowspan")

                if cell_3_rowspan:
                    # cells[3] is ownership with rowspan
                    hospital_data["ownership"] = self._clean_text(cells[3].text.strip())
                    # Beds are at position 4, staff at position 5
                    if len(cells) > 4:
                        hospital_data["beds"] = self._extract_number(
                            cells[4].text.strip()
                        )
                    if len(cells) > 5:
                        hospital_data["staff"] = self._extract_number(
                            cells[5].text.strip()
                        )
                else:
                    # cells[3] is beds (no rowspan ownership cell in this row)
                    # Ownership comes from rowspan of a previous row
                    hospital_data["beds"] = self._extract_number(cells[3].text.strip())
                    if len(cells) > 4:
                        hospital_data["staff"] = self._extract_number(
                            cells[4].text.strip()
                        )

        except Exception as e:
            logger.debug(f"Error parsing hospital row content: {e}")

        return hospital_data

    @staticmethod
    def _clean_text(text):
        """Clean text by removing references and extra whitespace"""
        # Remove Wikipedia reference markers like [4], [19], etc.
        text = re.sub(r"\[\d+\]", "", text)
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    @staticmethod
    def _extract_number(text):
        """Extract numeric value from text"""
        # Remove commas and extract first number
        text = text.replace(",", "")
        match = re.search(r"\d+", text)
        return match.group(0) if match else ""

    def to_dataframe(self):
        """Convert scraped hospitals to DataFrame"""
        df = pd.DataFrame(self.hospitals)
        logger.info(f"Converted {len(df)} hospitals to DataFrame")
        return df


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = HospitalsScraper(headless=True)
    url = "https://en.wikipedia.org/wiki/List_of_hospitals_in_Singapore"

    df = scraper.scrape(url)
    print(f"\nScraped {len(df)} hospitals")
    print("\nFirst few hospitals:")
    print(df.head(10))

    # Save to CSV
    scraper.save_to_csv("data/raw/hospitals.csv")
