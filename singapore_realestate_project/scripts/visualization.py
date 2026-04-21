"""
Visualization Script
Create interactive maps and visualizations
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, HeatMap
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from config import (
    MAPS_DIR, VISUALIZATIONS_DIR, SINGAPORE_CENTER,
    FOLIUM_ZOOM_START, FOLIUM_TILES
)

class Visualizer:
    """Create interactive visualizations and maps"""

    def __init__(self, df):
        self.df = df
        self.maps_dir = MAPS_DIR
        self.viz_dir = VISUALIZATIONS_DIR

    def create_property_map(self, title="Singapore Properties"):
        """Create interactive map of properties"""
        print(f"\nCreating property map: {title}...")

        # Create base map centered on Singapore
        m = folium.Map(
            location=SINGAPORE_CENTER,
            zoom_start=FOLIUM_ZOOM_START,
            tiles=FOLIUM_TILES
        )

        # Add property markers with clustering
        marker_cluster = MarkerCluster().add_to(m)

        for idx, row in self.df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                continue

            popup_text = f"<b>{row.get('property_type', 'Property')}</b><br>"
            if 'price' in row:
                popup_text += f"Price: ${row['price']:,.0f}<br>"
            if 'floor_area' in row:
                popup_text += f"Area: {row['floor_area']:.0f} sqm<br>"

            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                popup=folium.Popup(popup_text, max_width=250),
                color='blue',
                fill=True,
                fillColor='blue',
                fillOpacity=0.7
            ).add_to(marker_cluster)

        # Save map
        filepath = self.maps_dir / "properties_map.html"
        m.save(str(filepath))
        print(f"Saved to {filepath}")
        return m

    def create_amenities_map(self, schools_df=None, hospitals_df=None, mrt_df=None):
        """Create map with amenity locations"""
        print("\nCreating amenities map...")

        m = folium.Map(
            location=SINGAPORE_CENTER,
            zoom_start=FOLIUM_ZOOM_START,
            tiles=FOLIUM_TILES
        )

        # Add schools (green)
        if schools_df is not None and not schools_df.empty:
            for idx, row in schools_df.iterrows():
                if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')):
                    continue
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=3,
                    popup=row.get('name', 'School'),
                    color='green',
                    fill=True,
                    fillOpacity=0.7
                ).add_to(m)

        # Add hospitals (red)
        if hospitals_df is not None and not hospitals_df.empty:
            for idx, row in hospitals_df.iterrows():
                if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')):
                    continue
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=3,
                    popup=row.get('name', 'Hospital'),
                    color='red',
                    fill=True,
                    fillOpacity=0.7
                ).add_to(m)

        # Add MRT stations (orange)
        if mrt_df is not None and not mrt_df.empty:
            for idx, row in mrt_df.iterrows():
                if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')):
                    continue
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=4,
                    popup=row.get('name', 'MRT Station'),
                    color='orange',
                    fill=True,
                    fillOpacity=0.8
                ).add_to(m)

        # Add legend
        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; right: 50px; width: 180px; height: 150px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <p style="margin: 0;"><b>Legend</b></p>
        <p style="margin: 5px;"><i class="fa fa-circle" style="color:blue"></i> Properties</p>
        <p style="margin: 5px;"><i class="fa fa-circle" style="color:green"></i> Schools</p>
        <p style="margin: 5px;"><i class="fa fa-circle" style="color:red"></i> Hospitals</p>
        <p style="margin: 5px;"><i class="fa fa-circle" style="color:orange"></i> MRT Stations</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        filepath = self.maps_dir / "amenities_map.html"
        m.save(str(filepath))
        print(f"Saved to {filepath}")
        return m

    def create_price_heatmap(self):
        """Create heatmap of property prices"""
        print("\nCreating price heatmap...")

        # Check if required columns exist
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            print("Latitude/longitude columns required for heatmap")
            return None

        if 'price' not in self.df.columns:
            print("Price column required for heatmap")
            return None

        # Create base map
        m = folium.Map(
            location=SINGAPORE_CENTER,
            zoom_start=FOLIUM_ZOOM_START,
            tiles=FOLIUM_TILES
        )

        # Prepare heatmap data
        heat_data = []
        for idx, row in self.df.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']) and pd.notna(row['price']):
                # Normalize price to 0-1 for heatmap intensity
                heat_data.append([
                    row['latitude'],
                    row['longitude'],
                    row['price']
                ])

        if heat_data:
            # Find max price for normalization
            max_price = max([x[2] for x in heat_data])
            heat_data_normalized = [[x[0], x[1], x[2]/max_price] for x in heat_data]

            HeatMap(heat_data_normalized).add_to(m)

        filepath = self.maps_dir / "price_heatmap.html"
        m.save(str(filepath))
        print(f"Saved to {filepath}")
        return m

    def create_distance_analysis_plots(self):
        """Create plots analyzing distance relationships with price"""
        print("\nCreating distance analysis plots...")

        distance_cols = [col for col in self.df.columns if col.startswith('dist_to_')]

        if not distance_cols or 'price' not in self.df.columns:
            print("Distance and price columns required")
            return

        fig = make_subplots(
            rows=1, cols=len(distance_cols),
            subplot_titles=distance_cols
        )

        for idx, col in enumerate(distance_cols, 1):
            fig.add_trace(
                go.Scatter(
                    x=self.df[col],
                    y=self.df['price'],
                    mode='markers',
                    name=col,
                    marker=dict(size=5, opacity=0.6)
                ),
                row=1, col=idx
            )

        fig.update_xaxes(title_text="Distance (m)", row=1, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_layout(height=400, showlegend=False, title_text="Price vs Distance to Amenities")

        filepath = self.viz_dir / "distance_analysis.html"
        fig.write_html(str(filepath))
        print(f"Saved to {filepath}")

    def create_price_distribution_plots(self):
        """Create interactive price distribution plots"""
        print("\nCreating price distribution plots...")

        if 'price' not in self.df.columns:
            print("Price column required")
            return

        fig = make_subplots(specs=[[{"secondary_y": False}]])

        fig.add_trace(
            go.Histogram(x=self.df['price'], nbinsx=50, name='Price Distribution')
        )

        fig.update_layout(
            title_text="Price Distribution",
            xaxis_title="Price ($)",
            yaxis_title="Frequency",
            height=500
        )

        filepath = self.viz_dir / "price_distribution.html"
        fig.write_html(str(filepath))
        print(f"Saved to {filepath}")

    def create_amenity_count_analysis(self):
        """Analyze relationship between amenity counts and price"""
        print("\nCreating amenity count analysis...")

        amenity_cols = [col for col in self.df.columns if '_within_' in col]

        if not amenity_cols or 'price' not in self.df.columns:
            print("Amenity count and price columns required")
            return

        for col in amenity_cols[:3]:  # Limit to first 3
            fig = px.scatter(
                self.df,
                x=col,
                y='price',
                title=f"Price vs {col}",
                labels={col: f"Number of amenities {col}", 'price': 'Price ($)'}
            )
            fig.update_traces(marker=dict(size=5, opacity=0.6))

            filename = col.replace('_', ' ').replace('within', 'Within').lower()
            filepath = self.viz_dir / f"amenity_count_{col}.html"
            fig.write_html(str(filepath))
            print(f"Saved to {filepath}")

    def create_proximity_category_analysis(self):
        """Analyze price by proximity categories"""
        print("\nCreating proximity category analysis...")

        proximity_cols = [col for col in self.df.columns if '_proximity' in col]

        if not proximity_cols or 'price' not in self.df.columns:
            print("Proximity category and price columns required")
            return

        for col in proximity_cols:
            fig = px.box(
                self.df,
                x=col,
                y='price',
                title=f"Price by {col}",
                labels={col: col.replace('_', ' ').title(), 'price': 'Price ($)'}
            )

            filepath = self.viz_dir / f"price_by_{col}.html"
            fig.write_html(str(filepath))
            print(f"Saved to {filepath}")

    def run_full_visualization(self, schools_df=None, hospitals_df=None, mrt_df=None):
        """Run complete visualization workflow"""
        print("\n" + "=" * 60)
        print("STARTING VISUALIZATIONS")
        print("=" * 60)

        # Create maps
        self.create_property_map()
        self.create_amenities_map(schools_df, hospitals_df, mrt_df)
        self.create_price_heatmap()

        # Create analysis plots
        self.create_price_distribution_plots()
        self.create_distance_analysis_plots()
        self.create_amenity_count_analysis()
        self.create_proximity_category_analysis()

        print("\n" + "=" * 60)
        print("VISUALIZATIONS COMPLETE")
        print("=" * 60)
        print(f"Maps saved to {self.maps_dir}")
        print(f"Visualizations saved to {self.viz_dir}")

def main():
    """Main visualization workflow"""
    # TODO: Load data
    # df = pd.read_csv(PROCESSED_DATA_DIR / "properties_engineered.csv")
    # schools_df = pd.read_csv(PROCESSED_DATA_DIR / "schools_processed.csv")
    # hospitals_df = pd.read_csv(PROCESSED_DATA_DIR / "hospitals_processed.csv")
    # mrt_df = pd.read_csv(PROCESSED_DATA_DIR / "mrt_processed.csv")

    # visualizer = Visualizer(df)
    # visualizer.run_full_visualization(schools_df, hospitals_df, mrt_df)

    print("Visualization module ready. Implement data loading in main().")

if __name__ == "__main__":
    main()
