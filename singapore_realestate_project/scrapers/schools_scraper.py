"""
Singapore Schools Scraper

Scrapes school information from MOE SchoolFinder
https://www.moe.gov.sg/schoolfinder
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging
import time
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SchoolsScraper(BaseScraper):
    """Scraper for Singapore school data from MOE SchoolFinder"""

    def __init__(self, headless=True, implicit_wait=10):
        """Initialize schools scraper"""
        super().__init__(headless=headless, implicit_wait=implicit_wait)
        self.schools = []

    def scrape(self, url, school_types=None):
        """
        Scrape schools from MOE SchoolFinder

        Args:
            url: MOE SchoolFinder URL
            school_types: List of school types to scrape
                         ['preschool', 'primary', 'secondary', 'college', 'jc']
                         If None, scrapes all types

        Returns:
            pd.DataFrame: DataFrame containing school data
        """
        if school_types is None:
            school_types = ['preschool', 'primary', 'secondary', 'college', 'jc']

        self.setup_driver()
        try:
            self.get_page(url)
            self._accept_cookies()

            for school_type in school_types:
                logger.info(f"Scraping {school_type} schools...")
                self._scrape_school_type(school_type)

            return self.to_dataframe()
        finally:
            self.close_driver()

    def _accept_cookies(self):
        """Accept cookies if present"""
        try:
            # Look for cookie acceptance button
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

    def _scrape_school_type(self, school_type):
        """
        Scrape schools of a specific type

        Args:
            school_type: Type of school ('preschool', 'primary', 'secondary', 'college', 'jc')
        """
        try:
            # Click on school type filter/tab if available
            self._select_school_type(school_type)
            time.sleep(2)

            # Scroll and load all results
            self._load_all_results()

            # Extract schools from current view
            self._extract_schools_from_page(school_type)

        except Exception as e:
            logger.warning(f"Error scraping {school_type} schools: {e}")

    def _select_school_type(self, school_type):
        """Select school type from filters"""
        try:
            # Try different selector patterns for school type selection
            selectors = [
                f"//button[contains(text(), '{school_type.capitalize()}')]",
                f"//label[contains(text(), '{school_type.capitalize()}')]",
                f"//input[@value='{school_type}']",
            ]

            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    element.click()
                    logger.info(f"Selected {school_type}")
                    return
                except:
                    continue

            logger.warning(f"Could not find selector for {school_type}")
        except Exception as e:
            logger.warning(f"Error selecting school type {school_type}: {e}")

    def _load_all_results(self):
        """Load all results by scrolling and clicking 'Load More' if available"""
        try:
            max_scrolls = 10
            scroll_count = 0

            while scroll_count < max_scrolls:
                self.scroll_to_bottom()
                time.sleep(1)

                # Try to click "Load More" button
                try:
                    load_more = self.driver.find_element(
                        By.XPATH,
                        "//button[contains(text(), 'Load')] | //button[contains(text(), 'More')]"
                    )
                    self.driver.execute_script("arguments[0].click();", load_more)
                    logger.info("Clicked Load More")
                    time.sleep(2)
                except:
                    break

                scroll_count += 1
        except Exception as e:
            logger.debug(f"Error loading all results: {e}")

    def _extract_schools_from_page(self, school_type):
        """Extract school data from the page"""
        try:
            # Try different selectors for school cards/items
            school_selectors = [
                "div[class*='school-card']",
                "div[class*='school-item']",
                "li[class*='school']",
                "div[class*='result']",
                "div.result-item",
            ]

            school_elements = []
            for selector in school_selectors:
                try:
                    school_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if school_elements:
                        logger.info(f"Found {len(school_elements)} schools with selector: {selector}")
                        break
                except:
                    continue

            # If no elements found with CSS selectors, try generic XPath
            if not school_elements:
                school_elements = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(@class, 'school') or contains(@class, 'result')]"
                )

            logger.info(f"Total school elements found: {len(school_elements)}")

            for school_element in school_elements:
                try:
                    school_data = self._parse_school_element(school_element, school_type)
                    if school_data['name']:  # Only add if name exists
                        self.schools.append(school_data)
                        logger.debug(f"Extracted: {school_data['name']}")
                except Exception as e:
                    logger.debug(f"Error parsing school element: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error extracting schools from page: {e}")

    def _parse_school_element(self, element, school_type):
        """Parse a school element to extract data"""
        school_data = {
            'name': '',
            'type': school_type,
            'address': '',
            'contact': '',
            'principal': '',
            'url': ''
        }

        try:
            # Extract school name
            name_elem = element.find_element(
                By.CSS_SELECTOR,
                "h2, h3, [class*='name'], [class*='title']"
            )
            school_data['name'] = name_elem.text.strip()

            # Extract address
            address_selectors = [
                "[class*='address']",
                "p[class*='location']",
                "span[class*='address']"
            ]
            for selector in address_selectors:
                try:
                    addr_elem = element.find_element(By.CSS_SELECTOR, selector)
                    school_data['address'] = addr_elem.text.strip()
                    break
                except:
                    continue

            # Extract contact
            contact_selectors = [
                "[class*='phone']",
                "[class*='contact']",
                "a[href^='tel:']"
            ]
            for selector in contact_selectors:
                try:
                    contact_elem = element.find_element(By.CSS_SELECTOR, selector)
                    school_data['contact'] = contact_elem.text.strip()
                    break
                except:
                    continue

            # Extract URL if available
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[href]")
                school_data['url'] = link_elem.get_attribute('href')
            except:
                pass

        except Exception as e:
            logger.debug(f"Error parsing school element content: {e}")

        return school_data

    def to_dataframe(self):
        """Convert scraped schools to DataFrame"""
        df = pd.DataFrame(self.schools)
        logger.info(f"Converted {len(df)} schools to DataFrame")
        return df


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = SchoolsScraper(headless=True)
    url = "https://www.moe.gov.sg/schoolfinder"

    df = scraper.scrape(url, school_types=['primary', 'secondary'])
    print(f"\nScraped {len(df)} schools")
    print("\nFirst few schools:")
    print(df.head(10))

    # Save to CSV
    scraper.save_to_csv("data/raw/schools.csv")
