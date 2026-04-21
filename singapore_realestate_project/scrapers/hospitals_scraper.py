"""
Singapore Hospitals Scraper

Scrapes hospital information from SGDI
https://www.sgdi.gov.sg/other-organisations/hospitals
"""

from selenium.webdriver.common.by import By
import pandas as pd
import logging
import time
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HospitalsScraper(BaseScraper):
    """Scraper for Singapore hospital data from SGDI"""

    def __init__(self, headless=True, implicit_wait=10):
        """Initialize hospitals scraper"""
        super().__init__(headless=headless, implicit_wait=implicit_wait)
        self.hospitals = []

    def scrape(self, url):
        """
        Scrape hospitals from SGDI

        Args:
            url: SGDI hospitals URL

        Returns:
            pd.DataFrame: DataFrame containing hospital data
        """
        self.setup_driver()
        try:
            self.get_page(url)
            self._accept_cookies()
            self._extract_hospitals()
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

    def _extract_hospitals(self):
        """Extract hospital data from the page"""
        try:
            # Load all content by scrolling
            self._load_all_content()
            time.sleep(2)

            # Try different selectors for hospital items
            hospital_selectors = [
                "div[class*='hospital']",
                "div[class*='card']",
                "div[class*='item']",
                "li[class*='hospital']",
                "article",
            ]

            hospital_elements = []
            for selector in hospital_selectors:
                try:
                    hospital_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(hospital_elements) > 2:  # Filter out noise
                        logger.info(f"Found {len(hospital_elements)} hospitals with selector: {selector}")
                        break
                except:
                    continue

            logger.info(f"Total hospital elements: {len(hospital_elements)}")

            for hospital_elem in hospital_elements:
                try:
                    hospital_data = self._parse_hospital_element(hospital_elem)
                    if hospital_data['name']:
                        self.hospitals.append(hospital_data)
                        logger.debug(f"Extracted: {hospital_data['name']}")
                except Exception as e:
                    logger.debug(f"Error parsing hospital element: {e}")

        except Exception as e:
            logger.warning(f"Error extracting hospitals: {e}")

    def _load_all_content(self):
        """Load all content by scrolling and expanding sections"""
        try:
            for i in range(5):  # Scroll multiple times
                self.scroll_to_bottom()
                time.sleep(1)

                # Try to click any "Show More" or "Expand" buttons
                try:
                    expand_buttons = self.driver.find_elements(
                        By.XPATH,
                        "//button[contains(text(), 'More')] | //button[contains(text(), 'Expand')]"
                    )
                    for button in expand_buttons[:3]:  # Click first few
                        try:
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(0.5)
                        except:
                            pass
                except:
                    pass
        except Exception as e:
            logger.debug(f"Error loading all content: {e}")

    def _parse_hospital_element(self, element):
        """Parse a hospital element to extract data"""
        hospital_data = {
            'name': '',
            'address': '',
            'contact': '',
            'specialties': '',
            'bed_count': '',
            'url': ''
        }

        try:
            # Extract hospital name
            name_selectors = [
                "h2, h3, h4",
                "[class*='name']",
                "[class*='title']",
                "strong"
            ]

            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name_text = name_elem.text.strip()
                    if name_text and len(name_text) > 2:
                        hospital_data['name'] = name_text
                        break
                except:
                    continue

            # If no name found using CSS, try getting text from first paragraph
            if not hospital_data['name']:
                try:
                    text = element.text.split('\n')[0].strip()
                    if len(text) > 2:
                        hospital_data['name'] = text
                except:
                    pass

            # Extract address
            address_selectors = [
                "[class*='address']",
                "[class*='location']",
                "p"
            ]
            for selector in address_selectors:
                try:
                    addr_elem = element.find_element(By.CSS_SELECTOR, selector)
                    addr_text = addr_elem.text.strip()
                    # Check if it looks like an address (contains common keywords)
                    if any(keyword in addr_text.lower() for keyword in ['street', 'road', 'singapore', '64', '65', '66', '67', '68', '69']):
                        hospital_data['address'] = addr_text
                        break
                except:
                    continue

            # Extract contact information
            contact_selectors = [
                "[class*='phone']",
                "[class*='contact']",
                "a[href^='tel:']"
            ]
            for selector in contact_selectors:
                try:
                    contact_elem = element.find_element(By.CSS_SELECTOR, selector)
                    contact_text = contact_elem.text.strip()
                    if contact_text:
                        hospital_data['contact'] = contact_text
                        break
                except:
                    continue

            # Extract specialties if available
            specialty_selectors = [
                "[class*='specialt']",
                "[class*='service']"
            ]
            for selector in specialty_selectors:
                try:
                    spec_elem = element.find_element(By.CSS_SELECTOR, selector)
                    spec_text = spec_elem.text.strip()
                    if spec_text:
                        hospital_data['specialties'] = spec_text
                        break
                except:
                    continue

            # Extract URL if available
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[href]")
                hospital_data['url'] = link_elem.get_attribute('href')
            except:
                pass

            # Try to extract all text and look for patterns
            all_text = element.text.lower()

            # Look for bed count
            import re
            bed_match = re.search(r'(\d+)\s*(?:beds?|bed)', all_text)
            if bed_match:
                hospital_data['bed_count'] = bed_match.group(1)

        except Exception as e:
            logger.debug(f"Error parsing hospital element: {e}")

        return hospital_data


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = HospitalsScraper(headless=True)
    url = "https://www.sgdi.gov.sg/other-organisations/hospitals"

    df = scraper.scrape(url)
    print(f"\nScraped {len(df)} hospitals")
    print("\nFirst few hospitals:")
    print(df.head(10))

    # Save to CSV
    scraper.save_to_csv("data/raw/hospitals.csv")
