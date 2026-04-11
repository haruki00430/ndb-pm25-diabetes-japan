#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 2: HbA1c Data Extraction Script
======================================
Extract prefecture-level HbA1c mean values from NDB health checkup data.

Input:
    - NDB No.10 特定健診 検査: HbA1c 都道府県別性年齢階級別分布.xlsx

Output:
    - projects/NDB_XXX_PM25_diabetes/data/interim/hba1c_prefecture.csv

Processing:
    1. Read Excel file with MultiIndex header
    2. Extract HbA1c strata counts by prefecture
    3. Calculate weighted average using strata midpoints

Author: Claude Sonnet 4.5
Created: 2026-03-11
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
_log_file = _log_dir / '02_extract_hba1c.py.log'
logger = setup_logger(__name__, log_file=str(_log_file))


def load_config(config_path: str) -> dict:
    """Load project configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def parse_hba1c_data(file_path: Path, strata_midpoints: dict) -> pd.DataFrame:
    """
    Parse HbA1c Excel file and calculate prefecture-level weighted averages.

    Args:
        file_path: Path to HbA1c Excel file
        strata_midpoints: Dictionary mapping HbA1c strata to midpoint values

    Returns:
        DataFrame with columns: prefecture, hba1c_mean, total_count
    """
    logger.info('Parsing HbA1c Excel file')

    # Read with MultiIndex header (rows 2-3, 0-indexed)
    # Similar to chrono_nutrition questionnaire files
    df = pd.read_excel(file_path, sheet_name='HbA1C', header=[2, 3])

    logger.info(f'Raw data shape: {df.shape}')
    logger.info(f'Column names (first 5): {df.columns[:5].tolist()}')

    # Simplify column names
    df.columns = [f'{col[0]}_{col[1]}' if 'Unnamed' not in str(col[0])
                  else col[1] for col in df.columns]

    # Rename first two columns
    df.rename(columns={df.columns[0]: '都道府県', df.columns[1]: '検査値階層'}, inplace=True)

    logger.info(f'Renamed columns (first 5): {df.columns[:5].tolist()}')
    logger.info(f'First 15 rows of first 2 columns:\n{df[["都道府県", "検査値階層"]].head(15)}')

    # Remove rows where both columns are NaN
    df = df[df['検査値階層'].notna()].reset_index(drop=True)

    # Forward fill prefecture names
    df['都道府県'] = df['都道府県'].ffill()

    logger.info(f'After ffill, first 15 rows:\n{df[["都道府県", "検査値階層"]].head(15)}')

    # Numeric columns (sex × age groups)
    numeric_cols = [col for col in df.columns if col not in ['都道府県', '検査値階層']]

    logger.info(f'Number of numeric columns: {len(numeric_cols)}')

    # Convert '-' to NaN and then to numeric
    for col in numeric_cols:
        df[col] = df[col].replace('-', np.nan)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate prefecture-level weighted averages
    results = []

    for pref in df['都道府県'].unique():
        df_pref = df[df['都道府県'] == pref]

        logger.debug(f'\nProcessing {pref}:')
        logger.debug(f'  Strata found: {df_pref["検査値階層"].tolist()}')

        # Extract strata counts
        strata_counts = {}

        for _, row in df_pref.iterrows():
            strata = row['検査値階層']

            # Sum across all numeric columns
            count = row[numeric_cols].sum()

            if not pd.isna(count) and count > 0:
                strata_counts[strata] = count
                logger.debug(f'  {strata}: {count:,.0f}')

        # Calculate weighted average
        if len(strata_counts) > 0:
            total_count = sum(strata_counts.values())

            weighted_sum = sum(
                count * strata_midpoints.get(strata, 0)
                for strata, count in strata_counts.items()
            )

            hba1c_mean = weighted_sum / total_count if total_count > 0 else np.nan

            results.append({
                'prefecture': pref,
                'hba1c_mean': hba1c_mean,
                'total_count': total_count,
                'n_strata': len(strata_counts)
            })

            logger.info(f'{pref}: HbA1c={hba1c_mean:.3f}%, N={total_count:,.0f}, strata={len(strata_counts)}')
        else:
            logger.warning(f'{pref}: No valid strata data found')

    df_result = pd.DataFrame(results)

    if len(df_result) == 0:
        logger.error('No prefectures extracted!')
        raise ValueError('Failed to extract any prefecture data')

    # Exclude "都道府県判別不可" or similar invalid prefectures
    invalid_prefs = ['都道府県判別不可', '都道府県不明', '不明']
    df_result = df_result[~df_result['prefecture'].isin(invalid_prefs)].reset_index(drop=True)

    logger.info(f'\nExtracted {len(df_result)} valid prefectures')
    logger.info(f'HbA1c mean range: {df_result["hba1c_mean"].min():.3f} - {df_result["hba1c_mean"].max():.3f}%')

    return df_result


def main():
    """Main execution function."""
    logger.info('=' * 80)
    logger.info('Phase 2: HbA1c Data Extraction')
    logger.info('=' * 80)

    # Load configuration
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    config_path = project_dir / 'config' / 'config.yaml'
    config = load_config(str(config_path))
    logger.info(f'Loaded configuration from: {config_path}')

    # Get strata midpoints from config
    strata_midpoints = config['outcome_variables']['hba1c']['strata_midpoints']
    logger.info(f'HbA1c strata midpoints:')
    for strata, midpoint in strata_midpoints.items():
        logger.info(f'  {strata}: {midpoint}')

    # Define paths
    project_root = Path(__file__).resolve().parents[3]
    checkup_dir = project_root / config['input_paths']['checkup_examination']
    output_dir = project_root / config['output_paths']['interim']
    output_dir.mkdir(parents=True, exist_ok=True)

    # Input file
    hba1c_file = checkup_dir / config['outcome_variables']['hba1c']['file_name']

    logger.info(f'HbA1c file: {hba1c_file}')
    logger.info(f'Output dir: {output_dir}')

    # Check if file exists
    if not hba1c_file.exists():
        logger.error(f'HbA1c file not found: {hba1c_file}')
        raise FileNotFoundError(f'HbA1c file not found: {hba1c_file}')

    # Parse HbA1c data
    logger.info('-' * 80)

    df_hba1c = parse_hba1c_data(hba1c_file, strata_midpoints)

    # Display summary statistics
    logger.info('-' * 80)
    logger.info('Summary Statistics')
    logger.info('-' * 80)
    logger.info(f'Total prefectures: {len(df_hba1c)}')
    logger.info(f'\nHbA1c mean (%):')
    logger.info(f'  Mean: {df_hba1c["hba1c_mean"].mean():.3f}')
    logger.info(f'  Std:  {df_hba1c["hba1c_mean"].std():.3f}')
    logger.info(f'  Min:  {df_hba1c["hba1c_mean"].min():.3f}')
    logger.info(f'  Max:  {df_hba1c["hba1c_mean"].max():.3f}')
    logger.info(f'\nTotal count:')
    logger.info(f'  Mean: {df_hba1c["total_count"].mean():.0f}')
    logger.info(f'  Min:  {df_hba1c["total_count"].min():.0f}')
    logger.info(f'  Max:  {df_hba1c["total_count"].max():.0f}')

    # Top 5 highest/lowest HbA1c
    logger.info(f'\nTop 5 highest HbA1c:')
    for _, row in df_hba1c.nlargest(5, 'hba1c_mean').iterrows():
        logger.info(f'  {row["prefecture"]}: {row["hba1c_mean"]:.3f}%')

    logger.info(f'\nTop 5 lowest HbA1c:')
    for _, row in df_hba1c.nsmallest(5, 'hba1c_mean').iterrows():
        logger.info(f'  {row["prefecture"]}: {row["hba1c_mean"]:.3f}%')

    # Save output
    output_file = output_dir / 'hba1c_prefecture.csv'
    df_hba1c.to_csv(output_file, index=False, encoding='utf-8')
    logger.info('-' * 80)
    logger.info(f'Output saved to: {output_file}')
    logger.info(f'Shape: {df_hba1c.shape}')
    logger.info('-' * 80)

    logger.info('=' * 80)
    logger.info('Phase 2 completed successfully!')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
