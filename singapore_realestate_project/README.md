# Singapore Real Estate Analysis Project

## Project Overview
Analysis of Singapore real estate prices and their relationship to proximity of schools, hospitals, and MRT stations.

## Objectives
1. **Dataset Understanding**: Understand real estate market context and features
2. **Data Preprocessing**: Clean data, handle missing values, engineer features
3. **Exploratory Data Analysis**: Analyze distributions, relationships, and patterns
4. **Insights & Recommendations**: Provide actionable insights based on findings

## Tech Stack
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Web Scraping**: Selenium
- **Geolocation**: Google Maps API
- **EDA & Visualization**: Seaborn, Matplotlib, Plotly, Folium
- **Geographic Analysis**: GeoPandas
- **Notebooks**: Jupyter

## Project Structure
```
singapore_realestate_project/
├── data/                          # All datasets
│   ├── raw/                       # Raw data from sources
│   │   ├── hdb_resale.csv
│   │   ├── private_properties.csv
│   │   ├── schools.csv
│   │   ├── hospitals.csv
│   │   └── mrt_stations.csv
│   └── processed/                 # Cleaned and merged data
│       └── merged_dataset.csv
├── scripts/                       # Python scripts
│   ├── config.py                  # Configuration and constants
│   ├── data_collection.py         # Web scraping scripts
│   ├── data_preprocessing.py      # Data cleaning and preprocessing
│   ├── feature_engineering.py     # Distance calculations, feature creation
│   ├── eda.py                     # EDA functions and analysis
│   └── visualization.py           # Map and visualization functions
├── notebooks/                     # Jupyter notebooks
│   ├── 01_data_collection.ipynb
│   ├── 02_data_preprocessing.ipynb
│   ├── 03_eda.ipynb
│   └── 04_insights_visualization.ipynb
├── output/                        # Generated outputs
│   ├── visualizations/            # Charts, maps, plots
│   ├── reports/                   # Analysis reports
│   └── maps/                      # Interactive maps (HTML)
├── config/                        # Configuration files
│   └── settings.json              # API keys, paths, parameters
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create `.env` file in project root with:
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

Or edit `config/settings.json` with your API keys and paths.

### 4. Create Data Directories
```bash
mkdir -p data/raw data/processed output/visualizations output/reports output/maps
```

## Data Sources

### Real Estate Data
- **HDB Resale**: data.gov.sg (download CSV)
- **Private Properties**: PropertyGuru, EdgeProp (scrape with Selenium)
- **Kaggle Singapore Real Estate**: Pre-compiled datasets

### Location Data
- **Schools**: Ministry of Education (MOE) or OpenStreetMap
- **Hospitals**: Ministry of Health (MOH) or Google Maps API
- **MRT Stations**: LRT/MRT official data or OpenStreetMap

## Workflow

### Phase 1: Data Collection
- Download HDB data from data.gov.sg
- Scrape property portals with Selenium (if needed)
- Use Google Maps API to get coordinates for schools, hospitals, MRT

### Phase 2: Data Preprocessing
- Clean missing values, handle outliers
- Standardize address formats and coordinates
- Merge datasets on location

### Phase 3: Feature Engineering
- Calculate distances from each property to:
  - Nearest school
  - Nearest hospital
  - Nearest MRT station
- Aggregate proximity metrics (e.g., count within 500m radius)

### Phase 4: EDA
- Univariate analysis (distributions, summary stats)
- Bivariate analysis (relationships with price)
- Multivariate analysis (correlations, interactions)
- Visualizations (scatter plots, heatmaps, maps)

### Phase 5: Insights
- Identify key factors driving property prices
- Compare HDB vs private properties
- Analyze by district/region
- Provide recommendations

## Key Files

- `scripts/config.py` - Configuration, constants, and utilities
- `scripts/data_collection.py` - Web scraping and data download
- `scripts/data_preprocessing.py` - Data cleaning functions
- `scripts/feature_engineering.py` - Distance calculations
- `scripts/eda.py` - Analysis functions
- `scripts/visualization.py` - Plotting and mapping

## Running Analysis

### Using Jupyter Notebooks (Recommended for EDA)
```bash
jupyter notebook notebooks/
```

### Using Scripts
```bash
python scripts/data_collection.py
python scripts/data_preprocessing.py
python scripts/feature_engineering.py
python scripts/eda.py
```

## Output

Analysis outputs will be saved to:
- `output/visualizations/` - Charts and plots
- `output/maps/` - Interactive Folium maps
- `output/reports/` - Analysis summaries

## Notes
- Store sensitive data (API keys) in `.env` file, not in code
- Keep raw data in `data/raw/` - never modify it
- Use `data/processed/` for cleaned datasets
- Document assumptions and limitations in notebooks

## Contact
Email: haziqfaiz.ripin@gmail.com
