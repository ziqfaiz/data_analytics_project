"""
Data Preprocessing Script
Clean, transform, and prepare data for analysis
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

from config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, MISSING_VALUE_THRESHOLD,
    OUTLIER_METHOD, OUTLIER_THRESHOLD, COLUMN_MAPPING
)

class DataPreprocessor:
    """Preprocess and clean real estate data"""

    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
        self.processed_data_dir = PROCESSED_DATA_DIR

    def load_raw_data(self, filename):
        """Load raw data from CSV"""
        filepath = self.raw_data_dir / filename
        print(f"Loading {filename}...")
        try:
            df = pd.read_csv(filepath)
            print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None

    def handle_missing_values(self, df, threshold=MISSING_VALUE_THRESHOLD):
        """Handle missing values in dataframe"""
        print("\nHandling missing values...")

        # Drop columns with missing values above threshold
        missing_ratio = df.isnull().sum() / len(df)
        cols_to_drop = missing_ratio[missing_ratio > threshold].index
        df = df.drop(columns=cols_to_drop)
        print(f"Dropped {len(cols_to_drop)} columns with >{threshold*100}% missing values")

        # Fill remaining missing values
        for col in df.columns:
            if df[col].isnull().any():
                if df[col].dtype in ['float64', 'int64']:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown", inplace=True)

        print(f"Remaining missing values: {df.isnull().sum().sum()}")
        return df

    def handle_outliers(self, df, columns=None, method=OUTLIER_METHOD, threshold=OUTLIER_THRESHOLD):
        """Handle outliers in numerical columns"""
        print("\nHandling outliers...")

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns

        for col in columns:
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR

                # Cap outliers instead of removing
                df[col] = df[col].clip(lower_bound, upper_bound)
                print(f"  {col}: Capped outliers [{lower_bound:.2f}, {upper_bound:.2f}]")

            elif method == "zscore":
                from scipy import stats
                z_scores = np.abs(stats.zscore(df[col]))
                df[col] = df[col][(z_scores < threshold)]

        return df

    def standardize_column_names(self, df):
        """Standardize column names"""
        print("\nStandardizing column names...")
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        return df

    def encode_categorical(self, df, categorical_cols=None):
        """Encode categorical variables"""
        print("\nEncoding categorical variables...")

        if categorical_cols is None:
            categorical_cols = df.select_dtypes(include=['object']).columns

        for col in categorical_cols:
            if df[col].nunique() < 50:  # Only encode if reasonable number of categories
                le = LabelEncoder()
                df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
                print(f"  {col}: {df[col].nunique()} categories encoded")

        return df

    def normalize_numerical(self, df, numerical_cols=None, method='minmax'):
        """Normalize numerical features"""
        print("\nNormalizing numerical features...")

        if numerical_cols is None:
            numerical_cols = df.select_dtypes(include=[np.number]).columns

        if method == 'minmax':
            scaler = StandardScaler()
            df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
            print(f"  Normalized {len(numerical_cols)} columns using MinMax scaling")

        return df, numerical_cols

    def remove_duplicates(self, df):
        """Remove duplicate rows"""
        print("\nRemoving duplicates...")
        initial_rows = len(df)
        df = df.drop_duplicates()
        removed = initial_rows - len(df)
        print(f"  Removed {removed} duplicate rows")
        return df

    def data_quality_report(self, df):
        """Generate data quality report"""
        print("\n" + "=" * 60)
        print("DATA QUALITY REPORT")
        print("=" * 60)
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        print(f"\nMissing values:")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("  None")

        print(f"\nData types:")
        print(df.dtypes)

        print(f"\nBasic statistics:")
        print(df.describe())

    def preprocess_pipeline(self, df):
        """Run complete preprocessing pipeline"""
        print("\n" + "=" * 60)
        print("RUNNING PREPROCESSING PIPELINE")
        print("=" * 60)

        # Step 1: Standardize column names
        df = self.standardize_column_names(df)

        # Step 2: Remove duplicates
        df = self.remove_duplicates(df)

        # Step 3: Handle missing values
        df = self.handle_missing_values(df)

        # Step 4: Handle outliers (for numerical columns)
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        df = self.handle_outliers(df, columns=numerical_cols)

        # Step 5: Encode categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        df = self.encode_categorical(df, categorical_cols=categorical_cols)

        # Step 6: Data quality report
        self.data_quality_report(df)

        return df

    def merge_datasets(self, property_df, schools_df=None, hospitals_df=None, mrt_df=None):
        """
        Merge property data with location data
        TODO: Implement proper merging logic based on coordinates
        """
        print("\n" + "=" * 60)
        print("MERGING DATASETS")
        print("=" * 60)

        # This will be implemented in feature_engineering.py
        # For now, just merge on common columns if they exist

        return property_df

    def save_processed_data(self, df, filename):
        """Save processed data to CSV"""
        filepath = self.processed_data_dir / filename
        df.to_csv(filepath, index=False)
        print(f"\nSaved processed data to {filepath}")
        return filepath

def main():
    """Main preprocessing workflow"""
    preprocessor = DataPreprocessor()

    # Load raw data
    # hdb_df = preprocessor.load_raw_data("hdb_resale.csv")
    # schools_df = preprocessor.load_raw_data("schools.csv")
    # hospitals_df = preprocessor.load_raw_data("hospitals.csv")
    # mrt_df = preprocessor.load_raw_data("mrt_stations.csv")

    # TODO: Implement preprocessing for each dataset
    # hdb_df = preprocessor.preprocess_pipeline(hdb_df)

    # Merge datasets
    # merged_df = preprocessor.merge_datasets(hdb_df, schools_df, hospitals_df, mrt_df)

    # Save processed data
    # preprocessor.save_processed_data(merged_df, "merged_dataset.csv")

    print("Preprocessing module ready. Implement data loading in main().")

if __name__ == "__main__":
    main()
