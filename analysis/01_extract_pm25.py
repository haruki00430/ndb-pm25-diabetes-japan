#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 1: PM2.5 Data Extraction Script
======================================
Extract prefecture-level PM2.5 annual mean concentrations from NIES air pollution data.

Input:
    - 02_Data/raw/Air_Pollution/TD20221200.zip (2022 FY PM2.5 data)
    - 02_Data/raw/Air_Pollution/TD20231200.zip (2023 FY PM2.5 data)

Output:
    - projects/NDB_XXX_PM25_diabetes/data/interim/pm25_prefecture.csv

Processing:
    1. Extract ZIP files
    2. Read CSV files (Shift-JIS encoding)
    3. Aggregate by prefecture (mean of all measurement stations)
    4. Calculate 2-year average (2022-2023)

Author: Claude Sonnet 4.5
Created: 2026-03-11
"""

import pandas as pd
import zipfile
import yaml
from pathlib import Path
import logging
import sys

# Add project root to path for ndb_library import
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from ndb_library.logger import setup_logger

# Setup logger (will be created in the logs directory)
# Get script directory to construct log path
_script_dir = Path(__file__).resolve().parent
_log_dir = _script_dir / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / '01_extract_pm25.log'
logger = setup_logger(__name__, log_file=str(_log_file))


def load_config(config_path: str) -> dict:
    """
    Load project configuration from YAML file.

    Args:
        config_path: Path to config.yaml

    Returns:
        Dictionary containing configuration parameters
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def extract_zip(zip_path: Path, extract_to: Path, year: int) -> Path:
    """
    Extract ZIP file to specified directory.

    Args:
        zip_path: Path to ZIP file
        extract_to: Directory to extract files
        year: Year of data (used for unique subdirectory)

    Returns:
        Path to extracted text file
    """
    logger.info(f'Extracting ZIP file: {zip_path}')

    # Create year-specific subdirectory to avoid overwriting
    year_dir = extract_to / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(year_dir)

    # Find the extracted .txt file
    txt_files = list(year_dir.glob('*.txt'))
    if not txt_files:
        raise FileNotFoundError(f'No .txt file found in {year_dir}')

    txt_file = txt_files[0]
    logger.info(f'Extracted file: {txt_file}')
    return txt_file


def load_pm25_data(txt_file: Path) -> pd.DataFrame:
    """
    Load PM2.5 data from extracted text file.

    Args:
        txt_file: Path to extracted .txt file

    Returns:
        DataFrame containing PM2.5 measurement station data
    """
    logger.info(f'Reading PM2.5 data from: {txt_file}')

    # Read CSV with Shift-JIS encoding
    df = pd.read_csv(txt_file, encoding='shift-jis')

    logger.info(f'Loaded {len(df)} rows')
    logger.info(f'Columns: {df.columns.tolist()[:10]}...')  # Show first 10 columns

    return df


def aggregate_by_prefecture(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Aggregate PM2.5 data by prefecture.

    Args:
        df: DataFrame containing station-level PM2.5 data
        year: Year of data (for logging)

    Returns:
        DataFrame with prefecture-level aggregated data
        Columns: prefecture_code, prefecture_name, pm25_mean, n_stations
    """
    logger.info(f'Aggregating PM2.5 data by prefecture for year {year}')

    # Column indices based on README_DATA_STRUCTURE.md
    # 5: 都道府県コード (prefecture code)
    # 6: 都道府県名 (prefecture name)
    # Find column index for 年平均値(μg/m3)
    pm25_col = None
    for col in df.columns:
        if '年平均値' in str(col) and 'μg/m3' in str(col):
            pm25_col = col
            break

    if pm25_col is None:
        raise ValueError('年平均値(μg/m3) column not found')

    logger.info(f'Using column: {pm25_col} for PM2.5 annual mean')

    # Extract relevant columns
    prefecture_code_col = df.columns[5]  # 都道府県コード
    prefecture_name_col = df.columns[6]  # 都道府県名

    df_clean = df[[prefecture_code_col, prefecture_name_col, pm25_col]].copy()
    df_clean.columns = ['prefecture_code', 'prefecture_name', 'pm25_annual_mean']

    # Remove rows with missing PM2.5 values
    df_clean = df_clean.dropna(subset=['pm25_annual_mean'])

    logger.info(f'Valid rows after dropping NaN: {len(df_clean)}')

    # Aggregate by prefecture (mean of all stations)
    df_agg = df_clean.groupby(['prefecture_code', 'prefecture_name']).agg(
        pm25_mean=('pm25_annual_mean', 'mean'),
        n_stations=('pm25_annual_mean', 'count')
    ).reset_index()

    logger.info(f'Aggregated to {len(df_agg)} prefectures')
    logger.info(f'PM2.5 mean range: {df_agg["pm25_mean"].min():.2f} - {df_agg["pm25_mean"].max():.2f} μg/m3')
    logger.info(f'Number of stations range: {df_agg["n_stations"].min()} - {df_agg["n_stations"].max()}')

    return df_agg


def main():
    """
    Main execution function.
    """
    logger.info('=' * 80)
    logger.info('Phase 1: PM2.5 Data Extraction')
    logger.info('=' * 80)

    # Load configuration
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    config_path = project_dir / 'config' / 'config.yaml'
    config = load_config(str(config_path))
    logger.info(f'Loaded configuration from: {config_path}')

    # Define paths
    # Get project root (3 levels up from script: analysis -> project -> projects -> root)
    project_root = Path(__file__).resolve().parents[3]
    air_pollution_dir = project_root / config['input_paths']['air_pollution']
    output_dir = project_root / config['output_paths']['interim']
    temp_dir = project_dir / 'data' / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f'Project root: {project_root}')
    logger.info(f'Air pollution dir: {air_pollution_dir}')
    logger.info(f'Output dir: {output_dir}')
    logger.info(f'Temp dir: {temp_dir}')

    # Process 2022 data
    logger.info('-' * 80)
    logger.info('Processing 2022 FY data')
    logger.info('-' * 80)

    zip_2022 = air_pollution_dir / 'TD20221200.zip'
    txt_2022 = extract_zip(zip_2022, temp_dir, 2022)
    df_2022_raw = load_pm25_data(txt_2022)
    df_2022 = aggregate_by_prefecture(df_2022_raw, 2022)
    df_2022 = df_2022.rename(columns={
        'pm25_mean': 'pm25_mean_2022',
        'n_stations': 'n_stations_2022'
    })

    # Process 2023 data
    logger.info('-' * 80)
    logger.info('Processing 2023 FY data')
    logger.info('-' * 80)

    zip_2023 = air_pollution_dir / 'TD20231200.zip'
    txt_2023 = extract_zip(zip_2023, temp_dir, 2023)
    df_2023_raw = load_pm25_data(txt_2023)
    df_2023 = aggregate_by_prefecture(df_2023_raw, 2023)
    df_2023 = df_2023.rename(columns={
        'pm25_mean': 'pm25_mean_2023',
        'n_stations': 'n_stations_2023'
    })

    # Merge 2022 and 2023 data
    logger.info('-' * 80)
    logger.info('Merging 2022 and 2023 data')
    logger.info('-' * 80)

    df_merged = pd.merge(
        df_2022,
        df_2023[['prefecture_code', 'pm25_mean_2023', 'n_stations_2023']],
        on='prefecture_code',
        how='outer'
    )

    # Calculate 2-year average
    df_merged['pm25_mean_2yr'] = df_merged[['pm25_mean_2022', 'pm25_mean_2023']].mean(axis=1)

    # Check for missing data
    missing_2022 = df_merged['pm25_mean_2022'].isna().sum()
    missing_2023 = df_merged['pm25_mean_2023'].isna().sum()

    if missing_2022 > 0:
        logger.warning(f'{missing_2022} prefectures missing 2022 data')
    if missing_2023 > 0:
        logger.warning(f'{missing_2023} prefectures missing 2023 data')

    # Sort by prefecture code
    df_merged = df_merged.sort_values('prefecture_code').reset_index(drop=True)

    # Display summary statistics
    logger.info('-' * 80)
    logger.info('Summary Statistics')
    logger.info('-' * 80)
    logger.info(f'Total prefectures: {len(df_merged)}')
    logger.info(f'\n2022 PM2.5 mean (μg/m3):')
    logger.info(f'  Mean: {df_merged["pm25_mean_2022"].mean():.2f}')
    logger.info(f'  Min:  {df_merged["pm25_mean_2022"].min():.2f}')
    logger.info(f'  Max:  {df_merged["pm25_mean_2022"].max():.2f}')
    logger.info(f'\n2023 PM2.5 mean (μg/m3):')
    logger.info(f'  Mean: {df_merged["pm25_mean_2023"].mean():.2f}')
    logger.info(f'  Min:  {df_merged["pm25_mean_2023"].min():.2f}')
    logger.info(f'  Max:  {df_merged["pm25_mean_2023"].max():.2f}')
    logger.info(f'\n2-year average PM2.5 mean (μg/m3):')
    logger.info(f'  Mean: {df_merged["pm25_mean_2yr"].mean():.2f}')
    logger.info(f'  Min:  {df_merged["pm25_mean_2yr"].min():.2f}')
    logger.info(f'  Max:  {df_merged["pm25_mean_2yr"].max():.2f}')

    # Save output
    output_file = output_dir / 'pm25_prefecture.csv'
    output_dir.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(output_file, index=False, encoding='utf-8')
    logger.info('-' * 80)
    logger.info(f'Output saved to: {output_file}')
    logger.info(f'Shape: {df_merged.shape}')
    logger.info('-' * 80)

    # Clean up temporary files
    logger.info('Cleaning up temporary files')
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    logger.info('Temporary directory removed')

    logger.info('=' * 80)
    logger.info('Phase 1 completed successfully!')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
