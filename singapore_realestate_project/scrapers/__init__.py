"""
Web Scraping Module
Contains Selenium-based scrapers for various data sources and property portals
"""

from .base_scraper import BaseScraper
from .propertyguru_scraper import PropertyGuruScraper
from .edgeprop_scraper import EdgePropScraper
from .mrt_scraper import MRTScraper
from .schools_scraper import SchoolsScraper
from .hospitals_scraper import HospitalsScraper
from .ura_realestate_scraper import URARealestateScraper
from .scraper_manager import ScraperManager

__all__ = [
    'BaseScraper',
    'PropertyGuruScraper',
    'EdgePropScraper',
    'MRTScraper',
    'SchoolsScraper',
    'HospitalsScraper',
    'URARealestateScraper',
    'ScraperManager'
]
