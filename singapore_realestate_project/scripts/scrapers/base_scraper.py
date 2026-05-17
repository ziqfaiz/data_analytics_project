"""
Base Scraper Class
Parent class for all property portal scrapers
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for web scrapers using Selenium"""

    def __init__(self, headless=True, implicit_wait=10):
        """
        Initialize base scraper

        Args:
            headless: Run browser in headless mode
            implicit_wait: Implicit wait time in seconds
        """
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.driver = None
        self.properties = []

    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        logger.info("Setting up Chrome WebDriver...")

        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(self.implicit_wait)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def get_page(self, url):
        """Navigate to URL"""
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise

    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {value}")
            return None

    def find_elements(self, by, value):
        """Find multiple elements"""
        try:
            elements = self.driver.find_elements(by, value)
            return elements
        except NoSuchElementException:
            logger.warning(f"No elements found: {value}")
            return []

    def extract_text(self, element, by, value, default=""):
        """Safely extract text from element"""
        try:
            text_element = element.find_element(by, value)
            return text_element.text.strip()
        except NoSuchElementException:
            return default

    def extract_attribute(self, element, by, value, attribute, default=""):
        """Safely extract attribute from element"""
        try:
            attr_element = element.find_element(by, value)
            return attr_element.get_attribute(attribute) or default
        except NoSuchElementException:
            return default

    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        logger.info("Scrolling to bottom of page...")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def scroll_into_view(self, element):
        """Scroll element into view"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)

    def get_current_url(self):
        """Get current page URL"""
        return self.driver.current_url

    def get_page_source(self):
        """Get current page source"""
        return self.driver.page_source

    def take_screenshot(self, filename):
        """Take screenshot of current page"""
        filepath = Path(f"screenshots/{filename}.png")
        filepath.parent.mkdir(exist_ok=True)
        self.driver.save_screenshot(str(filepath))
        logger.info(f"Screenshot saved to {filepath}")

    def to_dataframe(self):
        """Convert scraped properties to DataFrame"""
        df = pd.DataFrame(self.properties)
        logger.info(f"Converted {len(df)} properties to DataFrame")
        return df

    def save_to_csv(self, filename):
        """Save scraped data to CSV"""
        df = self.to_dataframe()
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        return df

    def scrape(self, url, **kwargs):
        """
        Main scraping method (to be overridden by subclasses)

        Args:
            url: URL to scrape
            **kwargs: Additional arguments for specific scrapers
        """
        raise NotImplementedError("Subclasses must implement scrape() method")
