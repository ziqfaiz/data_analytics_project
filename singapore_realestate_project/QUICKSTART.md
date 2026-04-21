# Quick Start Guide

## Project Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy `.env.example` to `.env` and add your Google Maps API key:
```bash
cp .env.example .env
# Edit .env with your API key
```

### 3. Create Data Directories
```bash
mkdir -p data/raw data/processed output/visualizations output/reports output/maps
```

## Workflow Overview

### Phase 1: Data Collection (Week 1)
- **Notebook**: `notebooks/01_data_collection.ipynb`
- **Script**: `scripts/data_collection.py`
- **Tasks**:
  - Download HDB resale data from data.gov.sg
  - Get school/hospital/MRT locations
  - Optional: Scrape property portals with Selenium
- **Output**: CSV files in `data/raw/`

### Phase 2: Data Preprocessing (Week 2)
- **Script**: `scripts/data_preprocessing.py`
- **Tasks**:
  - Handle missing values
  - Remove outliers
  - Encode categorical variables
  - Standardize column names
- **Output**: Cleaned CSV in `data/processed/`

### Phase 3: Feature Engineering (Week 2)
- **Script**: `scripts/feature_engineering.py`
- **Tasks**:
  - Calculate distances to schools/hospitals/MRT
  - Count amenities within radius
  - Create categorical features
  - Create aggregate features
- **Output**: Engineered data with new features

### Phase 4: Exploratory Data Analysis (Week 3)
- **Notebook**: `notebooks/03_eda.ipynb`
- **Script**: `scripts/eda.py`
- **Tasks**:
  - Univariate analysis (distributions)
  - Bivariate analysis (relationships)
  - Create visualizations
  - Identify patterns
- **Output**: Charts and insights

### Phase 5: Insights & Visualization (Week 3-4)
- **Notebook**: `notebooks/04_insights_visualization.ipynb`
- **Script**: `scripts/visualization.py`
- **Tasks**:
  - Create interactive maps (Folium)
  - Analyze price vs distance relationships
  - Generate insights and recommendations
  - Create final report
- **Output**: Maps, visualizations, insights

## Key Files

| File | Purpose |
|------|---------|
| `scripts/config.py` | Configuration, paths, API keys |
| `scripts/data_collection.py` | Download and scrape data |
| `scripts/data_preprocessing.py` | Clean and transform data |
| `scripts/feature_engineering.py` | Create derived features |
| `scripts/eda.py` | Exploratory analysis functions |
| `scripts/visualization.py` | Maps and interactive plots |

## Running Analysis

### Option 1: Using Jupyter Notebooks (Recommended)
```bash
jupyter notebook notebooks/
```

### Option 2: Using Python Scripts
```bash
python scripts/data_collection.py
python scripts/data_preprocessing.py
python scripts/feature_engineering.py
python scripts/eda.py
python scripts/visualization.py
```

## Important Notes

1. **Data Sources**:
   - Primary: data.gov.sg (HDB, schools, hospitals)
   - Secondary: Kaggle for pre-compiled datasets
   - Google Maps API for coordinates

2. **API Key**:
   - Get free Google Maps API key from Google Cloud Console
   - Add to `.env` file before running

3. **Data Storage**:
   - `data/raw/` - Original data (never modify)
   - `data/processed/` - Cleaned data
   - `output/` - All outputs (maps, visualizations, reports)

4. **Output**:
   - Maps: `output/maps/` (HTML files)
   - Charts: `output/visualizations/` (PNG and HTML)
   - Reports: `output/reports/` (Text and markdown)

## Troubleshooting

**Missing data files?**
- Check `data/raw/` directory
- Download from data.gov.sg or Kaggle
- See data_collection.ipynb for links

**API key errors?**
- Verify `.env` file exists with correct key
- Check Google Cloud Console for API quota

**Import errors?**
- Run `pip install -r requirements.txt`
- Verify virtual environment is activated

## Next Steps

1. Read `README.md` for detailed project overview
2. Start with `notebooks/01_data_collection.ipynb`
3. Follow the workflow phases in order
4. Document your findings as you go
5. Focus on generating insights in Phase 5

Good luck with your analysis! 📊
