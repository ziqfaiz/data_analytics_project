"""
Configuration and settings for Singapore Real Estate Analysis Project
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"
VISUALIZATIONS_DIR = OUTPUT_DIR / "visualizations"
MAPS_DIR = OUTPUT_DIR / "maps"
REPORTS_DIR = OUTPUT_DIR / "reports"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, VISUALIZATIONS_DIR, MAPS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys and credentials
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "your_api_key_here")

# Singapore Coordinates (center of Singapore)
SINGAPORE_CENTER = (1.3521, 103.8198)
SINGAPORE_BBOX = {
    "north": 1.4754,
    "south": 1.2241,
    "east": 104.0856,
    "west": 103.6278
}

# Data sources URLs
DATA_SOURCES = {
    "hdb_resale": {
        "name": "HDB Resale Transactions",
        "url": "https://data.gov.sg/datasets",
        "source": "HDB"
    },
    "private_properties": {
        "name": "Private Property Sales",
        "url": "https://www.propertyguru.com.sg/",
        "source": "PropertyGuru (scrape)"
    },
    "schools": {
        "name": "School Locations",
        "url": "https://data.gov.sg/",
        "source": "MOE Data"
    },
    "hospitals": {
        "name": "Hospital Locations",
        "url": "https://data.gov.sg/",
        "source": "MOH Data"
    },
    "mrt_stations": {
        "name": "MRT Station Locations",
        "url": "https://data.gov.sg/",
        "source": "LRT/MRT Official"
    }
}

# Distance thresholds (in meters)
DISTANCE_THRESHOLDS = {
    "school": [500, 1000, 2000],      # meters
    "hospital": [500, 1000, 2000],    # meters
    "mrt": [300, 500, 1000]           # meters for MRT (usually walk distance)
}

# Data cleaning parameters
MISSING_VALUE_THRESHOLD = 0.5  # Drop columns with >50% missing
OUTLIER_METHOD = "iqr"          # IQR or zscore
OUTLIER_THRESHOLD = 1.5         # IQR multiplier

# Preprocessing settings
CATEGORICAL_COLUMNS = []        # Fill in after data exploration
NUMERICAL_COLUMNS = []          # Fill in after data exploration
TARGET_VARIABLE = "price"       # Price is the target

# EDA settings
CORRELATION_THRESHOLD = 0.3     # Show correlations above this
SAMPLE_SIZE_FOR_PLOTS = 5000    # Sample size for large plots

# Visualization settings
PLOT_STYLE = "seaborn-v0_8-darkgrid"
FIGURE_DPI = 300
FIGURE_SIZE = (12, 6)

# Folium map settings
FOLIUM_ZOOM_START = 12
FOLIUM_TILES = "OpenStreetMap"  # or "CartoDB positron"

# Column names mapping (standardize across sources)
COLUMN_MAPPING = {
    "price": ["price", "sale_price", "unit_price"],
    "latitude": ["lat", "latitude", "y"],
    "longitude": ["lon", "longitude", "x"],
    "location": ["location", "address", "location_name"],
    "property_type": ["property_type", "type", "unit_type"],
    "floor_area": ["floor_area", "area", "size_sqm"]
}

# Common property types
PROPERTY_TYPES = ["HDB", "Private Apartment", "Landed House", "Condo", "Landed Property"]

# Singapore regions/districts for analysis
SINGAPORE_REGIONS = [
    "Central", "East", "North", "North-East", "West"
]

def get_file_path(directory, filename):
    """Get full file path for a data file"""
    if directory == "raw":
        return RAW_DATA_DIR / filename
    elif directory == "processed":
        return PROCESSED_DATA_DIR / filename
    elif directory == "output":
        return OUTPUT_DIR / filename
    else:
        raise ValueError(f"Unknown directory: {directory}")

def print_config():
    """Print configuration summary"""
    print("=" * 60)
    print("PROJECT CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Raw Data: {RAW_DATA_DIR}")
    print(f"Processed Data: {PROCESSED_DATA_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Google Maps API Key: {'SET' if GOOGLE_MAPS_API_KEY != 'your_api_key_here' else 'NOT SET'}")
    print(f"Singapore Center: {SINGAPORE_CENTER}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()
