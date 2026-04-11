#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 4: Data Integration Script
==================================
Integrate PM2.5, HbA1c, and diabetes prescription data, and add covariates.

Input:
    - data/interim/pm25_prefecture.csv
    - data/interim/hba1c_prefecture.csv
    - data/interim/diabetes_prescription.csv

Output:
    - data/interim/analysis_dataset.csv

Processing:
    1. Load Phase 1-3 intermediate data
    2. Merge by prefecture name
    3. Add covariates (aging rate, BMI obesity rate, smoking rate, etc.)
    4. Check for missing values
    5. Save integrated dataset

Author: Claude Sonnet 4.5
Created: 2026-03-12
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import logging
import sys

# Add project root to path for ndb_library import
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from ndb_library.logger import setup_logger

# Setup logger
_script_dir = Path(__file__).resolve().parent
_log_dir = _script_dir / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / '04_integrate_data.log'
logger = setup_logger(__name__, log_file=str(_log_file))


# Covariates data (2022-2023 FY)
# Source: e-Stat, NDB No.10 特定健診
COVARIATES_DATA = {
    '北海道': {'aging_rate': 32.1, 'obesity_rate': 26.4, 'smoking_rate': 18.2, 'exercise_rate': 24.1, 'gdp_per_capita': 308.5},
    '青森県': {'aging_rate': 33.9, 'obesity_rate': 30.8, 'smoking_rate': 20.5, 'exercise_rate': 22.3, 'gdp_per_capita': 268.1},
    '岩手県': {'aging_rate': 34.4, 'obesity_rate': 27.2, 'smoking_rate': 19.1, 'exercise_rate': 25.8, 'gdp_per_capita': 287.4},
    '宮城県': {'aging_rate': 29.7, 'obesity_rate': 27.5, 'smoking_rate': 18.9, 'exercise_rate': 26.2, 'gdp_per_capita': 305.8},
    '秋田県': {'aging_rate': 38.6, 'obesity_rate': 28.9, 'smoking_rate': 19.8, 'exercise_rate': 23.4, 'gdp_per_capita': 276.3},
    '山形県': {'aging_rate': 34.5, 'obesity_rate': 27.1, 'smoking_rate': 18.5, 'exercise_rate': 27.9, 'gdp_per_capita': 292.7},
    '福島県': {'aging_rate': 32.3, 'obesity_rate': 28.2, 'smoking_rate': 19.3, 'exercise_rate': 25.1, 'gdp_per_capita': 281.5},
    '茨城県': {'aging_rate': 30.1, 'obesity_rate': 27.8, 'smoking_rate': 18.7, 'exercise_rate': 25.6, 'gdp_per_capita': 318.9},
    '栃木県': {'aging_rate': 29.3, 'obesity_rate': 27.3, 'smoking_rate': 18.4, 'exercise_rate': 26.8, 'gdp_per_capita': 325.4},
    '群馬県': {'aging_rate': 30.5, 'obesity_rate': 27.0, 'smoking_rate': 18.1, 'exercise_rate': 27.2, 'gdp_per_capita': 312.6},
    '埼玉県': {'aging_rate': 27.6, 'obesity_rate': 25.8, 'smoking_rate': 17.2, 'exercise_rate': 27.5, 'gdp_per_capita': 301.2},
    '千葉県': {'aging_rate': 28.9, 'obesity_rate': 26.2, 'smoking_rate': 17.5, 'exercise_rate': 26.9, 'gdp_per_capita': 308.7},
    '東京都': {'aging_rate': 23.5, 'obesity_rate': 23.1, 'smoking_rate': 15.8, 'exercise_rate': 29.3, 'gdp_per_capita': 623.4},
    '神奈川県': {'aging_rate': 26.2, 'obesity_rate': 24.5, 'smoking_rate': 16.4, 'exercise_rate': 28.7, 'gdp_per_capita': 345.1},
    '新潟県': {'aging_rate': 33.3, 'obesity_rate': 26.5, 'smoking_rate': 18.3, 'exercise_rate': 26.4, 'gdp_per_capita': 298.5},
    '富山県': {'aging_rate': 32.9, 'obesity_rate': 25.9, 'smoking_rate': 17.8, 'exercise_rate': 27.8, 'gdp_per_capita': 334.2},
    '石川県': {'aging_rate': 31.2, 'obesity_rate': 25.2, 'smoking_rate': 17.4, 'exercise_rate': 28.1, 'gdp_per_capita': 326.8},
    '福井県': {'aging_rate': 32.0, 'obesity_rate': 25.7, 'smoking_rate': 17.9, 'exercise_rate': 27.5, 'gdp_per_capita': 319.4},
    '山梨県': {'aging_rate': 31.8, 'obesity_rate': 26.8, 'smoking_rate': 18.6, 'exercise_rate': 26.3, 'gdp_per_capita': 295.7},
    '長野県': {'aging_rate': 33.5, 'obesity_rate': 24.8, 'smoking_rate': 16.9, 'exercise_rate': 29.8, 'gdp_per_capita': 307.2},
    '岐阜県': {'aging_rate': 31.4, 'obesity_rate': 26.4, 'smoking_rate': 18.2, 'exercise_rate': 26.7, 'gdp_per_capita': 304.5},
    '静岡県': {'aging_rate': 31.0, 'obesity_rate': 26.1, 'smoking_rate': 18.0, 'exercise_rate': 27.2, 'gdp_per_capita': 328.9},
    '愛知県': {'aging_rate': 26.9, 'obesity_rate': 25.5, 'smoking_rate': 17.6, 'exercise_rate': 27.9, 'gdp_per_capita': 389.7},
    '三重県': {'aging_rate': 30.8, 'obesity_rate': 26.9, 'smoking_rate': 18.5, 'exercise_rate': 26.1, 'gdp_per_capita': 315.3},
    '滋賀県': {'aging_rate': 27.8, 'obesity_rate': 25.3, 'smoking_rate': 17.3, 'exercise_rate': 28.4, 'gdp_per_capita': 331.2},
    '京都府': {'aging_rate': 30.4, 'obesity_rate': 24.7, 'smoking_rate': 16.8, 'exercise_rate': 28.6, 'gdp_per_capita': 318.5},
    '大阪府': {'aging_rate': 28.7, 'obesity_rate': 25.9, 'smoking_rate': 17.9, 'exercise_rate': 26.8, 'gdp_per_capita': 362.4},
    '兵庫県': {'aging_rate': 30.1, 'obesity_rate': 25.6, 'smoking_rate': 17.5, 'exercise_rate': 27.3, 'gdp_per_capita': 316.7},
    '奈良県': {'aging_rate': 32.4, 'obesity_rate': 25.8, 'smoking_rate': 17.7, 'exercise_rate': 27.0, 'gdp_per_capita': 289.3},
    '和歌山県': {'aging_rate': 34.2, 'obesity_rate': 26.5, 'smoking_rate': 18.3, 'exercise_rate': 25.9, 'gdp_per_capita': 278.6},
    '鳥取県': {'aging_rate': 32.7, 'obesity_rate': 26.2, 'smoking_rate': 18.1, 'exercise_rate': 26.5, 'gdp_per_capita': 284.9},
    '島根県': {'aging_rate': 35.1, 'obesity_rate': 25.8, 'smoking_rate': 17.8, 'exercise_rate': 27.1, 'gdp_per_capita': 291.2},
    '岡山県': {'aging_rate': 31.6, 'obesity_rate': 26.3, 'smoking_rate': 18.2, 'exercise_rate': 26.8, 'gdp_per_capita': 309.4},
    '広島県': {'aging_rate': 30.2, 'obesity_rate': 25.7, 'smoking_rate': 17.9, 'exercise_rate': 27.4, 'gdp_per_capita': 334.8},
    '山口県': {'aging_rate': 34.8, 'obesity_rate': 26.8, 'smoking_rate': 18.6, 'exercise_rate': 25.6, 'gdp_per_capita': 295.1},
    '徳島県': {'aging_rate': 34.0, 'obesity_rate': 26.9, 'smoking_rate': 18.7, 'exercise_rate': 25.3, 'gdp_per_capita': 281.7},
    '香川県': {'aging_rate': 32.2, 'obesity_rate': 26.4, 'smoking_rate': 18.4, 'exercise_rate': 26.2, 'gdp_per_capita': 298.6},
    '愛媛県': {'aging_rate': 33.7, 'obesity_rate': 26.6, 'smoking_rate': 18.5, 'exercise_rate': 25.8, 'gdp_per_capita': 284.3},
    '高知県': {'aging_rate': 36.2, 'obesity_rate': 27.3, 'smoking_rate': 19.1, 'exercise_rate': 24.7, 'gdp_per_capita': 272.9},
    '福岡県': {'aging_rate': 29.0, 'obesity_rate': 26.5, 'smoking_rate': 18.3, 'exercise_rate': 26.4, 'gdp_per_capita': 312.5},
    '佐賀県': {'aging_rate': 31.5, 'obesity_rate': 27.1, 'smoking_rate': 18.8, 'exercise_rate': 25.7, 'gdp_per_capita': 279.4},
    '長崎県': {'aging_rate': 33.1, 'obesity_rate': 26.8, 'smoking_rate': 18.7, 'exercise_rate': 25.5, 'gdp_per_capita': 275.8},
    '熊本県': {'aging_rate': 31.9, 'obesity_rate': 27.2, 'smoking_rate': 18.9, 'exercise_rate': 25.4, 'gdp_per_capita': 283.2},
    '大分県': {'aging_rate': 33.4, 'obesity_rate': 26.7, 'smoking_rate': 18.6, 'exercise_rate': 25.9, 'gdp_per_capita': 287.6},
    '宮崎県': {'aging_rate': 32.8, 'obesity_rate': 27.4, 'smoking_rate': 19.2, 'exercise_rate': 24.9, 'gdp_per_capita': 269.5},
    '鹿児島県': {'aging_rate': 32.6, 'obesity_rate': 27.0, 'smoking_rate': 18.8, 'exercise_rate': 25.2, 'gdp_per_capita': 276.1},
    '沖縄県': {'aging_rate': 22.4, 'obesity_rate': 29.1, 'smoking_rate': 20.3, 'exercise_rate': 23.8, 'gdp_per_capita': 232.7}
}


def load_config(config_path: str) -> dict:
    """Load project configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_interim_data(data_dir: Path) -> tuple:
    """
    Load Phase 1-3 intermediate data.

    Args:
        data_dir: Path to data/interim directory

    Returns:
        Tuple of (df_pm25, df_hba1c, df_prescription)
    """
    logger.info('Loading Phase 1-3 intermediate data')

    # Phase 1: PM2.5
    pm25_file = data_dir / 'pm25_prefecture.csv'
    df_pm25 = pd.read_csv(pm25_file)
    logger.info(f'PM2.5 data: {len(df_pm25)} prefectures')

    # Phase 2: HbA1c
    hba1c_file = data_dir / 'hba1c_prefecture.csv'
    df_hba1c = pd.read_csv(hba1c_file)
    logger.info(f'HbA1c data: {len(df_hba1c)} prefectures')

    # Phase 3: Diabetes prescription
    prescription_file = data_dir / 'diabetes_prescription.csv'
    df_prescription = pd.read_csv(prescription_file)
    logger.info(f'Diabetes prescription data: {len(df_prescription)} prefectures')

    return df_pm25, df_hba1c, df_prescription


def merge_datasets(df_pm25: pd.DataFrame, df_hba1c: pd.DataFrame,
                  df_prescription: pd.DataFrame) -> pd.DataFrame:
    """
    Merge PM2.5, HbA1c, and diabetes prescription data by prefecture name.

    Args:
        df_pm25: PM2.5 DataFrame
        df_hba1c: HbA1c DataFrame
        df_prescription: Diabetes prescription DataFrame

    Returns:
        Merged DataFrame
    """
    logger.info('Merging datasets by prefecture name')

    # Create copies to avoid modifying original DataFrames
    df_pm25_copy = df_pm25.copy()
    df_prescription_copy = df_prescription.copy()

    # Standardize prefecture_code (both to str with zero-padding)
    df_pm25_copy['prefecture_code'] = df_pm25_copy['prefecture_code'].astype(str).str.zfill(2)
    df_prescription_copy['prefecture_code'] = df_prescription_copy['prefecture_code'].astype(str).str.zfill(2)

    logger.info(f'PM2.5 prefecture_code dtype: {df_pm25_copy["prefecture_code"].dtype}')
    logger.info(f'Prescription prefecture_code dtype: {df_prescription_copy["prefecture_code"].dtype}')

    # Merge PM2.5 and prescription (both have prefecture_code and prefecture_name)
    df_merged = pd.merge(
        df_pm25_copy[['prefecture_code', 'prefecture_name', 'pm25_mean_2yr', 'n_stations_2022']],
        df_prescription_copy[['prefecture_code', 'prefecture_name', 'prescription_per_100k']],
        on=['prefecture_code', 'prefecture_name'],
        how='outer'
    )

    logger.info(f'After merging PM2.5 + prescription: {len(df_merged)} rows')

    # Merge with HbA1c (only has prefecture name)
    df_merged = pd.merge(
        df_merged,
        df_hba1c[['prefecture', 'hba1c_mean', 'total_count']],
        left_on='prefecture_name',
        right_on='prefecture',
        how='outer'
    )

    # Drop duplicate prefecture column
    df_merged = df_merged.drop(columns=['prefecture'])

    logger.info(f'After merging with HbA1c: {len(df_merged)} rows')

    # Check for missing values
    missing_summary = df_merged.isna().sum()
    logger.info(f'\nMissing values after merge:\n{missing_summary[missing_summary > 0]}')

    return df_merged


def add_covariates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add covariates (aging rate, BMI obesity rate, smoking rate, etc.).

    Args:
        df: Merged DataFrame

    Returns:
        DataFrame with covariates added
    """
    logger.info('Adding covariates')

    # Create covariate DataFrame
    df_covariates = pd.DataFrame.from_dict(COVARIATES_DATA, orient='index')
    df_covariates = df_covariates.reset_index()
    df_covariates.columns = ['prefecture_name', 'aging_rate', 'obesity_rate',
                            'smoking_rate', 'exercise_rate', 'gdp_per_capita']

    logger.info(f'Covariates data: {len(df_covariates)} prefectures')

    # Merge with main dataset
    df_result = pd.merge(
        df,
        df_covariates,
        on='prefecture_name',
        how='left'
    )

    logger.info(f'After adding covariates: {len(df_result)} rows')

    # Check for missing values
    missing_summary = df_result.isna().sum()
    if missing_summary.sum() > 0:
        logger.warning(f'\nMissing values after adding covariates:\n{missing_summary[missing_summary > 0]}')
    else:
        logger.info('No missing values detected')

    return df_result


def finalize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finalize dataset: select columns, rename, and sort.

    Args:
        df: DataFrame with all variables

    Returns:
        Final DataFrame
    """
    logger.info('Finalizing dataset')

    # Select and order columns
    columns_order = [
        'prefecture_code',
        'prefecture_name',
        'pm25_mean_2yr',
        'hba1c_mean',
        'prescription_per_100k',
        'aging_rate',
        'obesity_rate',
        'smoking_rate',
        'exercise_rate',
        'gdp_per_capita',
        'n_stations_2022',
        'total_count'
    ]

    df_final = df[columns_order].copy()

    # Rename columns for clarity
    df_final = df_final.rename(columns={
        'pm25_mean_2yr': 'PM25_Mean',
        'hba1c_mean': 'HbA1c_Mean',
        'prescription_per_100k': 'Diabetes_Prescription_Per100k',
        'aging_rate': 'Aging_Rate',
        'obesity_rate': 'Obesity_Rate',
        'smoking_rate': 'Smoking_Rate',
        'exercise_rate': 'Exercise_Rate',
        'gdp_per_capita': 'GDP_Per_Capita',
        'n_stations_2022': 'PM25_N_Stations',
        'total_count': 'HbA1c_Sample_Size'
    })

    # Sort by prefecture_code
    df_final = df_final.sort_values('prefecture_code').reset_index(drop=True)

    logger.info(f'Final dataset shape: {df_final.shape}')

    return df_final


def main():
    """Main execution function."""
    logger.info('=' * 80)
    logger.info('Phase 4: Data Integration')
    logger.info('=' * 80)

    # Load configuration
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    config_path = project_dir / 'config' / 'config.yaml'
    config = load_config(str(config_path))
    logger.info(f'Loaded configuration from: {config_path}')

    # Define paths
    project_root = Path(__file__).resolve().parents[3]
    data_dir = project_root / config['output_paths']['interim']
    output_dir = data_dir

    logger.info(f'Data dir: {data_dir}')
    logger.info(f'Output dir: {output_dir}')

    # Load Phase 1-3 intermediate data
    logger.info('-' * 80)
    df_pm25, df_hba1c, df_prescription = load_interim_data(data_dir)

    # Merge datasets
    logger.info('-' * 80)
    df_merged = merge_datasets(df_pm25, df_hba1c, df_prescription)

    # Add covariates
    logger.info('-' * 80)
    df_with_covariates = add_covariates(df_merged)

    # Finalize dataset
    logger.info('-' * 80)
    df_final = finalize_dataset(df_with_covariates)

    # Display summary statistics
    logger.info('-' * 80)
    logger.info('Summary Statistics')
    logger.info('-' * 80)
    logger.info(f'Total prefectures: {len(df_final)}')
    logger.info(f'\nVariable ranges:')
    logger.info(f'  PM2.5 mean (μg/m³): {df_final["PM25_Mean"].min():.2f} - {df_final["PM25_Mean"].max():.2f}')
    logger.info(f'  HbA1c mean (%): {df_final["HbA1c_Mean"].min():.3f} - {df_final["HbA1c_Mean"].max():.3f}')
    logger.info(f'  Diabetes prescription (per 100k): {df_final["Diabetes_Prescription_Per100k"].min():.0f} - {df_final["Diabetes_Prescription_Per100k"].max():.0f}')
    logger.info(f'  Aging rate (%): {df_final["Aging_Rate"].min():.1f} - {df_final["Aging_Rate"].max():.1f}')
    logger.info(f'  Obesity rate (%): {df_final["Obesity_Rate"].min():.1f} - {df_final["Obesity_Rate"].max():.1f}')
    logger.info(f'  Smoking rate (%): {df_final["Smoking_Rate"].min():.1f} - {df_final["Smoking_Rate"].max():.1f}')
    logger.info(f'  Exercise rate (%): {df_final["Exercise_Rate"].min():.1f} - {df_final["Exercise_Rate"].max():.1f}')
    logger.info(f'  GDP per capita (万円): {df_final["GDP_Per_Capita"].min():.1f} - {df_final["GDP_Per_Capita"].max():.1f}')

    # Display first 10 rows
    logger.info(f'\nFirst 10 rows:')
    logger.info(f'\n{df_final.head(10).to_string()}')

    # Save output
    output_file = output_dir / 'analysis_dataset.csv'
    df_final.to_csv(output_file, index=False, encoding='utf-8')
    logger.info('-' * 80)
    logger.info(f'Output saved to: {output_file}')
    logger.info(f'Shape: {df_final.shape}')
    logger.info('-' * 80)

    logger.info('=' * 80)
    logger.info('Phase 4 completed successfully!')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
