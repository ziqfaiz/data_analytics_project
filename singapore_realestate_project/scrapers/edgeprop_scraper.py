"""
EdgeProp Scraper
Scrape property listings from EdgeProp Singapore
"""

from selenium.webdriver.common.by import By
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class EdgePropScraper(BaseScraper):
    """Scraper for EdgeProp Singapore"""

    def __init__(self, headless=True):
        super().__init__(headless=headless)
        self.base_url = "https://www.edgeprop.sg"
        self.property_type = None
        self.region = None

    def scrape(self, url, max_pages=5, **kwargs):
        """
        Scrape EdgeProp listings

        Args:
            url: EdgeProp search URL
            max_pages: Maximum number of pages to scrape
            **kwargs: Additional parameters
        """
        try:
            self.setup_driver()
            logger.info(f"Starting EdgeProp scrape from {url}")

            for page in range(1, max_pages + 1):
                logger.info(f"Scraping page {page}...")

                # Navigate to page
                page_url = f"{url}?p={page}" if page > 1 else url
                self.get_page(page_url)

                # Extract properties
                self.extract_listings()

                # Check if next page exists
                if not self._has_next_page():
                    logger.info("Reached last page")
                    break

            logger.info(f"Scraped {len(self.properties)} properties total")
            return self.to_dataframe()

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return None
        finally:
            self.close_driver()

    def extract_listings(self):
        """Extract individual property listings from current page"""
        try:
            # TODO: Update selectors based on EdgeProp's actual HTML structure
            listing_cards = self.find_elements(By.CSS_SELECTOR, ".property-item, [data-testid='property-listing']")

            for card in listing_cards:
                try:
                    property_data = self._extract_property_data(card)
                    if property_data:
                        self.properties.append(property_data)
                except Exception as e:
                    logger.warning(f"Error extracting property: {e}")

            logger.info(f"Extracted {len(listing_cards)} listings from page")

        except Exception as e:
            logger.error(f"Error extracting listings: {e}")

    def _extract_property_data(self, card):
        """Extract data from a single property card"""
        try:
            # Example extraction (CUSTOMIZE based on actual HTML)
            property_data = {
                'title': self.extract_text(card, By.CSS_SELECTOR, ".property-name, h3", ""),
                'price': self._extract_price(card),
                'location': self.extract_text(card, By.CSS_SELECTOR, ".location, .address", ""),
                'property_type': self.extract_text(card, By.CSS_SELECTOR, ".property-type", ""),
                'floor_area': self._extract_floor_area(card),
                'bedrooms': self._extract_bedrooms(card),
                'url': self.extract_attribute(card, By.CSS_SELECTOR, "a", "href", ""),
                'source': 'EdgeProp'
            }
            return property_data
        except Exception as e:
            logger.warning(f"Error extracting property data: {e}")
            return None

    def _extract_price(self, card):
        """Extract price from property card"""
        try:
            price_text = self.extract_text(card, By.CSS_SELECTOR, ".price, .asking-price", "")
            # Remove currency symbols and convert to float
            price_text = price_text.replace('$', '').replace(',', '').replace('K', '000').strip()
            return float(price_text) if price_text else None
        except:
            return None

    def _extract_floor_area(self, card):
        """Extract floor area from property card"""
        try:
            area_text = self.extract_text(card, By.CSS_SELECTOR, ".floor-area, .sqft", "")
            area_text = area_text.split()[0].replace(',', '')
            return float(area_text) if area_text else None
        except:
            return None

    def _extract_bedrooms(self, card):
        """Extract number of bedrooms"""
        try:
            bedroom_text = self.extract_text(card, By.CSS_SELECTOR, ".bedrooms, .rooms", "")
            return int(bedroom_text.split()[0]) if bedroom_text else None
        except:
            return None

    def _has_next_page(self):
        """Check if next page button exists and is enabled"""
        try:
            next_button = self.find_elements(By.CSS_SELECTOR, ".next, [rel='next']")
            return len(next_button) > 0 and next_button[0].is_enabled()
        except:
            return False
