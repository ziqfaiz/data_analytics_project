"""
Feature Engineering Script
Calculate distances and create derived features
"""

import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import geopandas as gpd
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

from config import PROCESSED_DATA_DIR, DISTANCE_THRESHOLDS

class FeatureEngineer:
    """Create and engineer features for analysis"""

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate great circle distance between two points
        on earth (specified in decimal degrees)

        Returns distance in meters
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Radius of earth in meters

        return c * r

    @staticmethod
    def calculate_distance_to_nearest(property_lat, property_lon, locations_df, location_type="school"):
        """
        Calculate distance to nearest location of a given type

        Args:
            property_lat, property_lon: Property coordinates
            locations_df: DataFrame with locations and their coordinates
            location_type: Type of location (school, hospital, mrt)

        Returns:
            Distance in meters
        """
        if locations_df.empty:
            return np.nan

        min_distance = float('inf')

        for idx, row in locations_df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                continue

            dist = FeatureEngineer.haversine_distance(
                property_lat, property_lon,
                row['latitude'], row['longitude']
            )

            if dist < min_distance:
                min_distance = dist

        return min_distance if min_distance != float('inf') else np.nan

    @staticmethod
    def count_locations_within_radius(property_lat, property_lon, locations_df, radius=500):
        """
        Count number of locations within specified radius

        Args:
            property_lat, property_lon: Property coordinates
            locations_df: DataFrame with locations
            radius: Radius in meters

        Returns:
            Count of locations within radius
        """
        if locations_df.empty:
            return 0

        count = 0

        for idx, row in locations_df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                continue

            dist = FeatureEngineer.haversine_distance(
                property_lat, property_lon,
                row['latitude'], row['longitude']
            )

            if dist <= radius:
                count += 1

        return count

    def engineer_distance_features(self, properties_df, schools_df, hospitals_df, mrt_df):
        """
        Calculate distance features for all properties

        Args:
            properties_df: DataFrame with property data and coordinates
            schools_df, hospitals_df, mrt_df: Location DataFrames

        Returns:
            properties_df with new distance features
        """
        print("\n" + "=" * 60)
        print("ENGINEERING DISTANCE FEATURES")
        print("=" * 60)

        # Distance to nearest school
        print("Calculating distance to nearest school...")
        properties_df['dist_to_school_nearest'] = properties_df.apply(
            lambda row: self.calculate_distance_to_nearest(
                row['latitude'], row['longitude'], schools_df, 'school'
            ),
            axis=1
        )

        # Distance to nearest hospital
        print("Calculating distance to nearest hospital...")
        properties_df['dist_to_hospital_nearest'] = properties_df.apply(
            lambda row: self.calculate_distance_to_nearest(
                row['latitude'], row['longitude'], hospitals_df, 'hospital'
            ),
            axis=1
        )

        # Distance to nearest MRT
        print("Calculating distance to nearest MRT...")
        properties_df['dist_to_mrt_nearest'] = properties_df.apply(
            lambda row: self.calculate_distance_to_nearest(
                row['latitude'], row['longitude'], mrt_df, 'mrt'
            ),
            axis=1
        )

        # Count locations within radius
        for threshold in DISTANCE_THRESHOLDS['school']:
            col_name = f'schools_within_{threshold}m'
            print(f"Counting schools within {threshold}m...")
            properties_df[col_name] = properties_df.apply(
                lambda row: self.count_locations_within_radius(
                    row['latitude'], row['longitude'], schools_df, radius=threshold
                ),
                axis=1
            )

        for threshold in DISTANCE_THRESHOLDS['hospital']:
            col_name = f'hospitals_within_{threshold}m'
            print(f"Counting hospitals within {threshold}m...")
            properties_df[col_name] = properties_df.apply(
                lambda row: self.count_locations_within_radius(
                    row['latitude'], row['longitude'], hospitals_df, radius=threshold
                ),
                axis=1
            )

        for threshold in DISTANCE_THRESHOLDS['mrt']:
            col_name = f'mrt_within_{threshold}m'
            print(f"Counting MRT stations within {threshold}m...")
            properties_df[col_name] = properties_df.apply(
                lambda row: self.count_locations_within_radius(
                    row['latitude'], row['longitude'], mrt_df, radius=threshold
                ),
                axis=1
            )

        return properties_df

    @staticmethod
    def create_categorical_features(df):
        """Create categorical features from continuous variables"""
        print("\nCreating categorical features...")

        # Distance categories
        if 'dist_to_mrt_nearest' in df.columns:
            df['mrt_proximity'] = pd.cut(
                df['dist_to_mrt_nearest'],
                bins=[0, 500, 1000, 2000, float('inf')],
                labels=['Very Close', 'Close', 'Moderate', 'Far']
            )

        if 'dist_to_school_nearest' in df.columns:
            df['school_proximity'] = pd.cut(
                df['dist_to_school_nearest'],
                bins=[0, 500, 1000, 2000, float('inf')],
                labels=['Very Close', 'Close', 'Moderate', 'Far']
            )

        if 'dist_to_hospital_nearest' in df.columns:
            df['hospital_proximity'] = pd.cut(
                df['dist_to_hospital_nearest'],
                bins=[0, 500, 1000, 2000, float('inf')],
                labels=['Very Close', 'Close', 'Moderate', 'Far']
            )

        return df

    @staticmethod
    def create_aggregate_features(df):
        """Create aggregate proximity features"""
        print("\nCreating aggregate features...")

        # Total amenities within walkable distance (800m)
        amenity_cols = [col for col in df.columns if '_within_800m' in col or '_within_1000m' in col]
        if amenity_cols:
            df['total_amenities_nearby'] = df[amenity_cols].sum(axis=1)

        # Average distance to amenities
        distance_cols = [col for col in df.columns if col.startswith('dist_to_')]
        if distance_cols:
            df['avg_distance_to_amenities'] = df[distance_cols].mean(axis=1)

        return df

    @staticmethod
    def engineer_price_features(df):
        """Create price-related features"""
        print("\nCreating price-related features...")

        if 'price' in df.columns and 'floor_area' in df.columns:
            df['price_per_sqm'] = df['price'] / df['floor_area']
            print("  Created: price_per_sqm")

        if 'price' in df.columns:
            df['price_log'] = np.log(df['price'] + 1)
            print("  Created: price_log")

        return df

    @staticmethod
    def engineer_location_features(df):
        """Create location-based features"""
        print("\nCreating location features...")

        # Central vs non-central (if region data available)
        if 'region' in df.columns:
            central_regions = ['Central']
            df['is_central'] = df['region'].isin(central_regions).astype(int)
            print("  Created: is_central")

        return df

    def run_feature_engineering(self, properties_df, schools_df, hospitals_df, mrt_df):
        """Run complete feature engineering pipeline"""
        print("\n" + "=" * 60)
        print("RUNNING FEATURE ENGINEERING PIPELINE")
        print("=" * 60)

        # Step 1: Distance features
        properties_df = self.engineer_distance_features(
            properties_df, schools_df, hospitals_df, mrt_df
        )

        # Step 2: Categorical features
        properties_df = self.create_categorical_features(properties_df)

        # Step 3: Aggregate features
        properties_df = self.create_aggregate_features(properties_df)

        # Step 4: Price features
        properties_df = self.engineer_price_features(properties_df)

        # Step 5: Location features
        properties_df = self.engineer_location_features(properties_df)

        print("\n" + "=" * 60)
        print(f"Feature engineering complete. Created {len(properties_df.columns)} total features")
        print("=" * 60)

        return properties_df

    @staticmethod
    def save_engineered_data(df, filename):
        """Save engineered data"""
        filepath = PROCESSED_DATA_DIR / filename
        df.to_csv(filepath, index=False)
        print(f"\nSaved engineered data to {filepath}")
        return filepath

def main():
    """Main feature engineering workflow"""
    engineer = FeatureEngineer()

    # TODO: Load processed data
    # properties_df = pd.read_csv(PROCESSED_DATA_DIR / "properties_processed.csv")
    # schools_df = pd.read_csv(PROCESSED_DATA_DIR / "schools_processed.csv")
    # hospitals_df = pd.read_csv(PROCESSED_DATA_DIR / "hospitals_processed.csv")
    # mrt_df = pd.read_csv(PROCESSED_DATA_DIR / "mrt_processed.csv")

    # TODO: Run feature engineering
    # properties_df = engineer.run_feature_engineering(properties_df, schools_df, hospitals_df, mrt_df)
    # engineer.save_engineered_data(properties_df, "properties_engineered.csv")

    print("Feature engineering module ready. Implement data loading in main().")

if __name__ == "__main__":
    main()
