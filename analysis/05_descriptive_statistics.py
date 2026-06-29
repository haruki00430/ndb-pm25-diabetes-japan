#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 5: Descriptive Statistics & Exploratory Data Analysis (EDA)
==================================================================
Calculate descriptive statistics, correlation matrix, and create visualizations.

Input:
    - data/interim/analysis_dataset.csv

Output:
    - results/reports/descriptive_statistics.csv
    - results/reports/correlation_matrix.csv
    - results/figures/correlation_heatmap.png
    - results/figures/histograms.png
    - results/figures/scatterplot_matrix.png

Processing:
    1. Load integrated dataset
    2. Calculate descriptive statistics (mean, std, min, max, quartiles)
    3. Calculate correlation matrix (Pearson)
    4. Create visualizations (histograms, correlation heatmap)

Author: Claude Sonnet 4.5
Created: 2026-03-12
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path for ndb_library import
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from ndb_library.logger import setup_logger
from ndb_library.viz import set_japanese_font

# Setup logger
_script_dir = Path(__file__).resolve().parent
_log_dir = _script_dir / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / '05_descriptive_statistics.log'
logger = setup_logger(__name__, log_file=str(_log_file))


def load_config(config_path: str) -> dict:
    """Load project configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_analysis_dataset(data_file: Path) -> pd.DataFrame:
    """
    Load integrated analysis dataset.

    Args:
        data_file: Path to analysis_dataset.csv

    Returns:
        DataFrame with all variables
    """
    logger.info(f'Loading analysis dataset from: {data_file}')
    df = pd.read_csv(data_file)
    logger.info(f'Dataset shape: {df.shape}')
    logger.info(f'Columns: {df.columns.tolist()}')
    return df


def calculate_descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate descriptive statistics for all numeric variables.

    Args:
        df: Analysis dataset

    Returns:
        DataFrame with descriptive statistics
    """
    logger.info('Calculating descriptive statistics')

    # Select numeric columns (exclude prefecture_code and prefecture_name)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude ID columns
    exclude_cols = ['PM25_N_Stations', 'HbA1c_Sample_Size']
    analysis_cols = [col for col in numeric_cols if col not in exclude_cols]

    logger.info(f'Analyzing {len(analysis_cols)} numeric variables')

    # Calculate descriptive statistics
    desc_stats = df[analysis_cols].describe().T

    # Add additional statistics
    desc_stats['median'] = df[analysis_cols].median()
    desc_stats['IQR'] = desc_stats['75%'] - desc_stats['25%']
    desc_stats['CV'] = (desc_stats['std'] / desc_stats['mean']) * 100  # Coefficient of variation

    # Reorder columns
    desc_stats = desc_stats[['count', 'mean', 'std', 'median', 'IQR', 'CV',
                            'min', '25%', '50%', '75%', 'max']]

    logger.info(f'\nDescriptive statistics:\n{desc_stats.to_string()}')

    return desc_stats


def calculate_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Pearson correlation matrix for main variables.

    Args:
        df: Analysis dataset

    Returns:
        Correlation matrix DataFrame
    """
    logger.info('Calculating correlation matrix')

    # Select main variables for correlation analysis
    main_vars = [
        'PM25_Mean',
        'HbA1c_Mean',
        'Diabetes_Prescription_Per100k',
        'Aging_Rate',
        'Obesity_Rate',
        'Smoking_Rate',
        'Exercise_Rate',
        'GDP_Per_Capita'
    ]

    # Calculate correlation matrix
    corr_matrix = df[main_vars].corr()

    logger.info(f'\nCorrelation matrix:\n{corr_matrix.to_string()}')

    # Find strong correlations (|r| > 0.5) excluding diagonal
    strong_corr = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            r = corr_matrix.iloc[i, j]
            if abs(r) > 0.5:
                strong_corr.append({
                    'Variable 1': corr_matrix.columns[i],
                    'Variable 2': corr_matrix.columns[j],
                    'Correlation': r
                })

    if strong_corr:
        logger.info(f'\nStrong correlations (|r| > 0.5):')
        for item in strong_corr:
            logger.info(f"  {item['Variable 1']} <-> {item['Variable 2']}: r = {item['Correlation']:.3f}")
    else:
        logger.info('\nNo strong correlations (|r| > 0.5) detected')

    return corr_matrix


def create_histograms(df: pd.DataFrame, output_file: Path):
    """
    Create histograms for main variables.

    Args:
        df: Analysis dataset
        output_file: Path to save figure
    """
    logger.info('Creating histograms')

    # Select main variables
    main_vars = [
        ('PM25_Mean', 'Annual Mean PM2.5 (μg/m³)'),
        ('HbA1c_Mean', 'Mean HbA1c (%)'),
        ('Diabetes_Prescription_Per100k', 'Diabetes Medication Prescriptions (per 100k)'),
        ('Aging_Rate', 'Aging Rate (%)'),
        ('Obesity_Rate', 'Obesity Rate (%)'),
        ('Smoking_Rate', 'Smoking Rate (%)'),
        ('Exercise_Rate', 'Exercise Habit Rate (%)'),
        ('GDP_Per_Capita', 'GDP per Capita (10,000 JPY)')
    ]

    # Create figure with subplots
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    axes = axes.flatten()

    for i, (var, label) in enumerate(main_vars):
        ax = axes[i]
        ax.hist(df[var], bins=15, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel(label, fontsize=10)
        ax.set_ylabel('Number of Prefectures', fontsize=10)
        ax.set_title(f'Distribution of {label}', fontsize=11, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Add mean and median lines
        mean_val = df[var].mean()
        median_val = df[var].median()
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, label=f'Mean: {mean_val:.2f}')
        ax.axvline(median_val, color='green', linestyle='-.', linewidth=1.5, label=f'Median: {median_val:.2f}')
        ax.legend(fontsize=8)

    # Remove empty subplot
    fig.delaxes(axes[-1])

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f'Histograms saved to: {output_file}')


def create_correlation_heatmap(corr_matrix: pd.DataFrame, output_file: Path):
    """
    Create correlation heatmap.

    Args:
        corr_matrix: Correlation matrix
        output_file: Path to save figure
    """
    logger.info('Creating correlation heatmap')

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Rename variables for display (shorter labels)
    label_mapping = {
        'PM25_Mean': 'PM2.5',
        'HbA1c_Mean': 'HbA1c',
        'Diabetes_Prescription_Per100k': 'Diabetes Rx',
        'Aging_Rate': 'Aging Rate',
        'Obesity_Rate': 'Obesity Rate',
        'Smoking_Rate': 'Smoking Rate',
        'Exercise_Rate': 'Exercise Rate',
        'GDP_Per_Capita': 'GDP/capita'
    }

    corr_display = corr_matrix.rename(index=label_mapping, columns=label_mapping)

    # Create heatmap
    sns.heatmap(
        corr_display,
        annot=True,
        fmt='.3f',
        cmap='coolwarm',
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={'label': 'Pearson Correlation'},
        ax=ax
    )

    ax.set_title('Correlation Matrix of Prefecture-Level Variables', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f'Correlation heatmap saved to: {output_file}')


def create_scatterplot_matrix(df: pd.DataFrame, output_file: Path):
    """
    Create scatterplot matrix for main outcome variables.

    Args:
        df: Analysis dataset
        output_file: Path to save figure
    """
    logger.info('Creating scatterplot matrix')

    # Select key variables for scatterplot matrix
    key_vars = ['PM25_Mean', 'HbA1c_Mean', 'Diabetes_Prescription_Per100k', 'Aging_Rate']

    # Create pairplot
    g = sns.pairplot(
        df[key_vars],
        diag_kind='hist',
        plot_kws={'alpha': 0.6, 's': 50, 'edgecolor': 'k'},
        diag_kws={'bins': 15, 'edgecolor': 'k'}
    )

    # Rename axes labels
    label_mapping = {
        'PM25_Mean': 'PM2.5 (μg/m³)',
        'HbA1c_Mean': 'HbA1c (%)',
        'Diabetes_Prescription_Per100k': 'Diabetes Rx (per 100k)',
        'Aging_Rate': 'Aging Rate (%)'
    }

    for i in range(len(key_vars)):
        for j in range(len(key_vars)):
            ax = g.axes[i, j]
            if i == len(key_vars) - 1:
                ax.set_xlabel(label_mapping[key_vars[j]], fontsize=10)
            if j == 0:
                ax.set_ylabel(label_mapping[key_vars[i]], fontsize=10)

    g.fig.suptitle('Scatterplot Matrix of Key Variables', y=1.01, fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f'Scatterplot matrix saved to: {output_file}')


def main():
    """Main execution function."""
    logger.info('=' * 80)
    logger.info('Phase 5: Descriptive Statistics & EDA')
    logger.info('=' * 80)

    # Load configuration
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    config_path = project_dir / 'config' / 'config.yaml'
    config = load_config(str(config_path))
    logger.info(f'Loaded configuration from: {config_path}')

    # Define paths
    project_root = Path(__file__).resolve().parents[3]
    data_file = project_dir / 'data' / 'interim' / 'analysis_dataset.csv'
    results_dir = project_dir / 'results'
    reports_dir = results_dir / 'reports'
    figures_dir = results_dir / 'figures'

    # Create output directories
    reports_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f'Data file: {data_file}')
    logger.info(f'Reports dir: {reports_dir}')
    logger.info(f'Figures dir: {figures_dir}')

    # Load analysis dataset
    logger.info('-' * 80)
    df = load_analysis_dataset(data_file)

    # Calculate descriptive statistics
    logger.info('-' * 80)
    desc_stats = calculate_descriptive_statistics(df)

    # Save descriptive statistics
    desc_stats_file = reports_dir / 'descriptive_statistics.csv'
    desc_stats.to_csv(desc_stats_file, encoding='utf-8')
    logger.info(f'Descriptive statistics saved to: {desc_stats_file}')

    # Calculate correlation matrix
    logger.info('-' * 80)
    corr_matrix = calculate_correlation_matrix(df)

    # Save correlation matrix
    corr_matrix_file = reports_dir / 'correlation_matrix.csv'
    corr_matrix.to_csv(corr_matrix_file, encoding='utf-8')
    logger.info(f'Correlation matrix saved to: {corr_matrix_file}')

    # Create visualizations
    logger.info('-' * 80)
    logger.info('Creating visualizations')

    # 1. Histograms
    histograms_file = figures_dir / 'histograms.png'
    create_histograms(df, histograms_file)

    # 2. Correlation heatmap
    heatmap_file = figures_dir / 'correlation_heatmap.png'
    create_correlation_heatmap(corr_matrix, heatmap_file)

    # 3. Scatterplot matrix
    scatterplot_file = figures_dir / 'scatterplot_matrix.png'
    create_scatterplot_matrix(df, scatterplot_file)

    # Summary
    logger.info('-' * 80)
    logger.info('Summary')
    logger.info('-' * 80)
    logger.info(f'Total prefectures analyzed: {len(df)}')
    logger.info(f'\nOutput files created:')
    logger.info(f'  Reports:')
    logger.info(f'    - {desc_stats_file}')
    logger.info(f'    - {corr_matrix_file}')
    logger.info(f'  Figures:')
    logger.info(f'    - {histograms_file}')
    logger.info(f'    - {heatmap_file}')
    logger.info(f'    - {scatterplot_file}')

    logger.info('=' * 80)
    logger.info('Phase 5 completed successfully!')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
