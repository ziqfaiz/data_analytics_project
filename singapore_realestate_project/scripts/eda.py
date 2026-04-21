"""
Exploratory Data Analysis (EDA) Script
Perform univariate, bivariate, and multivariate analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from config import (
    VISUALIZATIONS_DIR, FIGURE_SIZE, FIGURE_DPI, PLOT_STYLE,
    CORRELATION_THRESHOLD
)

# Set plot style
plt.style.use(PLOT_STYLE)
sns.set_palette("husl")

class ExploratoryAnalysis:
    """Perform exploratory data analysis"""

    def __init__(self, df):
        self.df = df
        self.viz_dir = VISUALIZATIONS_DIR

    def univariate_analysis_numerical(self, columns=None):
        """Analyze numerical features"""
        print("\n" + "=" * 60)
        print("UNIVARIATE ANALYSIS - NUMERICAL FEATURES")
        print("=" * 60)

        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns

        for col in columns[:10]:  # Limit to first 10 for initial analysis
            print(f"\n{col}:")
            print(f"  Count: {self.df[col].count()}")
            print(f"  Mean: {self.df[col].mean():.2f}")
            print(f"  Median: {self.df[col].median():.2f}")
            print(f"  Std: {self.df[col].std():.2f}")
            print(f"  Min: {self.df[col].min():.2f}")
            print(f"  Max: {self.df[col].max():.2f}")
            print(f"  Skewness: {self.df[col].skew():.2f}")
            print(f"  Kurtosis: {self.df[col].kurtosis():.2f}")

    def univariate_analysis_categorical(self, columns=None):
        """Analyze categorical features"""
        print("\n" + "=" * 60)
        print("UNIVARIATE ANALYSIS - CATEGORICAL FEATURES")
        print("=" * 60)

        if columns is None:
            columns = self.df.select_dtypes(include=['object']).columns

        for col in columns[:5]:  # Limit to first 5
            print(f"\n{col}:")
            print(f"  Unique values: {self.df[col].nunique()}")
            print(f"  Top 5 values:")
            print(self.df[col].value_counts().head())

    def plot_distributions(self, numerical_cols=None):
        """Plot distributions of numerical features"""
        print("\nPlotting distributions...")

        if numerical_cols is None:
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns[:6]

        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        axes = axes.ravel()

        for idx, col in enumerate(numerical_cols):
            axes[idx].hist(self.df[col].dropna(), bins=50, edgecolor='black', alpha=0.7)
            axes[idx].set_title(f"Distribution of {col}")
            axes[idx].set_xlabel(col)
            axes[idx].set_ylabel("Frequency")

        plt.tight_layout()
        filepath = self.viz_dir / "distributions.png"
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        print(f"Saved to {filepath}")
        plt.close()

    def plot_boxplots(self, numerical_cols=None):
        """Plot boxplots for outlier detection"""
        print("\nPlotting boxplots...")

        if numerical_cols is None:
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns[:6]

        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        axes = axes.ravel()

        for idx, col in enumerate(numerical_cols):
            axes[idx].boxplot(self.df[col].dropna())
            axes[idx].set_title(f"Boxplot of {col}")
            axes[idx].set_ylabel(col)

        plt.tight_layout()
        filepath = self.viz_dir / "boxplots.png"
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        print(f"Saved to {filepath}")
        plt.close()

    def bivariate_analysis_numerical(self, target_col, numerical_cols=None, limit=5):
        """Analyze relationships between numerical features"""
        print("\n" + "=" * 60)
        print("BIVARIATE ANALYSIS - NUMERICAL FEATURES")
        print("=" * 60)

        if numerical_cols is None:
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns

        # Correlation with target
        if target_col in self.df.columns:
            print(f"\nCorrelation with {target_col}:")
            correlations = self.df[numerical_cols].corr()[target_col].sort_values(ascending=False)
            print(correlations)

    def plot_correlation_matrix(self, numerical_cols=None):
        """Plot correlation matrix heatmap"""
        print("\nPlotting correlation matrix...")

        if numerical_cols is None:
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns

        corr_matrix = self.df[numerical_cols].corr()

        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                    fmt='.2f', ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title("Correlation Matrix Heatmap")

        plt.tight_layout()
        filepath = self.viz_dir / "correlation_matrix.png"
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        print(f"Saved to {filepath}")
        plt.close()

    def plot_scatter_matrix(self, columns=None, sample_size=1000):
        """Plot scatter matrix for multiple relationships"""
        print("\nPlotting scatter matrix...")

        if columns is None:
            columns = list(self.df.select_dtypes(include=[np.number]).columns[:3])

        # Sample data if too large
        df_sample = self.df[columns].sample(n=min(sample_size, len(self.df)))

        sns.pairplot(df_sample, diag_kind='hist', plot_kws={'alpha': 0.6})
        filepath = self.viz_dir / "scatter_matrix.png"
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        print(f"Saved to {filepath}")
        plt.close()

    def plot_categorical_distributions(self, categorical_cols=None, limit=5):
        """Plot categorical variable distributions"""
        print("\nPlotting categorical distributions...")

        if categorical_cols is None:
            categorical_cols = self.df.select_dtypes(include=['object']).columns[:limit]

        fig, axes = plt.subplots(1, len(categorical_cols), figsize=(15, 4))
        if len(categorical_cols) == 1:
            axes = [axes]

        for idx, col in enumerate(categorical_cols):
            value_counts = self.df[col].value_counts().head(10)
            axes[idx].bar(range(len(value_counts)), value_counts.values)
            axes[idx].set_xticks(range(len(value_counts)))
            axes[idx].set_xticklabels(value_counts.index, rotation=45, ha='right')
            axes[idx].set_title(f"{col} Distribution")
            axes[idx].set_ylabel("Count")

        plt.tight_layout()
        filepath = self.viz_dir / "categorical_distributions.png"
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        print(f"Saved to {filepath}")
        plt.close()

    def plot_target_vs_features(self, target_col, numerical_cols=None, limit=6):
        """Plot target variable vs numerical features"""
        print(f"\nPlotting {target_col} vs features...")

        if target_col not in self.df.columns:
            print(f"Target column {target_col} not found!")
            return

        if numerical_cols is None:
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns

        numerical_cols = [col for col in numerical_cols if col != target_col][:limit]

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.ravel()

        for idx, col in enumerate(numerical_cols):
            axes[idx].scatter(self.df[col], self.df[target_col], alpha=0.5)
            axes[idx].set_xlabel(col)
            axes[idx].set_ylabel(target_col)
            axes[idx].set_title(f"{target_col} vs {col}")

        plt.tight_layout()
        filepath = self.viz_dir / f"{target_col}_vs_features.png"
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        print(f"Saved to {filepath}")
        plt.close()

    def generate_summary_statistics(self):
        """Generate summary statistics report"""
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)

        print("\nDataFrame Info:")
        print(f"Shape: {self.df.shape}")
        print(f"Memory usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        print("\nData Types:")
        print(self.df.dtypes.value_counts())

        print("\nMissing Values:")
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("None")

    def run_full_eda(self):
        """Run complete EDA workflow"""
        print("\n" + "=" * 60)
        print("STARTING EXPLORATORY DATA ANALYSIS")
        print("=" * 60)

        # Summary statistics
        self.generate_summary_statistics()

        # Univariate analysis
        self.univariate_analysis_numerical()
        self.univariate_analysis_categorical()

        # Visualizations
        self.plot_distributions()
        self.plot_boxplots()
        self.plot_correlation_matrix()
        self.plot_categorical_distributions()

        # Bivariate analysis with target
        if 'price' in self.df.columns:
            self.bivariate_analysis_numerical('price')
            self.plot_target_vs_features('price')

        print("\n" + "=" * 60)
        print("EDA COMPLETE")
        print("=" * 60)
        print(f"Visualizations saved to {self.viz_dir}")

def main():
    """Main EDA workflow"""
    # TODO: Load engineered data
    # df = pd.read_csv(PROCESSED_DATA_DIR / "properties_engineered.csv")
    # analyzer = ExploratoryAnalysis(df)
    # analyzer.run_full_eda()

    print("EDA module ready. Implement data loading in main().")

if __name__ == "__main__":
    main()
