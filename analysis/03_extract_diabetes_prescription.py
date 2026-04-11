#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 3: Diabetes Medication Data Extraction Script
====================================================
Extract prefecture-level diabetes medication prescription counts from NDB data.

Input:
    - NDB No.10 処方薬: 薬効分類396（糖尿病用剤）
    - 【内服】外来（院外）_都道府県別薬効分類別数量.xlsx
    - 【内服】外来（院内）_都道府県別薬効分類別数量.xlsx
    - 【内服】入院_都道府県別薬効分類別数量.xlsx
    - 【注射】都道府県別薬効分類別数量.xlsx

Output:
    - projects/NDB_XXX_PM25_diabetes/data/interim/diabetes_prescription.csv

Processing:
    1. Read 4 prescription files
    2. Filter by drug classification 396 (diabetes medications)
    3. Aggregate by prefecture
    4. Calculate per 100,000 population (using 2022 population data)

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
_log_file = _log_dir / '03_extract_diabetes_prescription.log'
logger = setup_logger(__name__, log_file=str(_log_file))


# Prefecture population data (2022, approximate in thousands)
# Source: e-Stat 人口推計 2022年10月1日現在
PREFECTURE_POPULATION_2022 = {
    '北海道': 5150, '青森県': 1208, '岩手県': 1194, '宮城県': 2281, '秋田県': 941,
    '山形県': 1047, '福島県': 1810, '茨城県': 2850, '栃木県': 1921, '群馬県': 1926,
    '埼玉県': 7350, '千葉県': 6284, '東京都': 14048, '神奈川県': 9237, '新潟県': 2161,
    '富山県': 1024, '石川県': 1122, '福井県': 762, '山梨県': 808, '長野県': 2033,
    '岐阜県': 1966, '静岡県': 3602, '愛知県': 7542, '三重県': 1760, '滋賀県': 1414,
    '京都府': 2562, '大阪府': 8809, '兵庫県': 5441, '奈良県': 1312, '和歌山県': 914,
    '鳥取県': 551, '島根県': 665, '岡山県': 1875, '広島県': 2780, '山口県': 1324,
    '徳島県': 715, '香川県': 946, '愛媛県': 1318, '高知県': 683, '福岡県': 5104,
    '佐賀県': 806, '長崎県': 1289, '熊本県': 1731, '大分県': 1118, '宮崎県': 1062,
    '鹿児島県': 1573, '沖縄県': 1468
}


def load_config(config_path: str) -> dict:
    """Load project configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_prescription_file(file_path: Path, drug_class: int = 396) -> pd.DataFrame:
    """
    Load prescription Excel file and extract drug classification data.

    File structure (based on NDB_DATA_VERIFICATION_REPORT.md):
    - Row 0: Title
    - Row 1: Empty
    - Row 2: Header (薬効分類, 薬効分類名称, ..., 総計, 01-47)
    - Row 3: Prefecture names (01=北海道, ..., 47=沖縄県)
    - Rows 4+: Data (each drug × prefecture counts)

    Args:
        file_path: Path to prescription Excel file
        drug_class: Drug classification code (default: 396 for diabetes)

    Returns:
        DataFrame with prefecture-level prescription counts
        Columns: prefecture_code, prefecture_name, prescription_count
    """
    logger.info(f'Reading prescription file: {file_path.name}')

    # Read Excel file with header at row 2 (0-indexed)
    df = pd.read_excel(file_path, header=2)

    logger.info(f'Raw data shape: {df.shape}')
    logger.info(f'Columns (first 15): {df.columns[:15].tolist()}')

    # Filter by drug classification
    # Assuming first column is '薬効分類'
    drug_class_col = df.columns[0]
    logger.info(f'Drug classification column: {drug_class_col}')

    df_filtered = df[df[drug_class_col] == drug_class].copy()

    logger.info(f'Rows after filtering by drug class {drug_class}: {len(df_filtered)}')

    if len(df_filtered) == 0:
        logger.warning(f'No data found for drug class {drug_class}')
        return pd.DataFrame(columns=['prefecture_code', 'prefecture_name', 'prescription_count'])

    # Extract prefecture columns
    # Based on NDB structure: columns 8+ are prefecture codes (総計 + 01-47)
    # We'll identify columns that are numeric (prefecture codes)

    # Get all columns after the first 8 metadata columns
    prefecture_cols = df.columns[8:]  # Skip metadata columns

    logger.info(f'Found {len(prefecture_cols)} potential prefecture columns')
    logger.info(f'Prefecture columns (first 10): {prefecture_cols[:10].tolist()}')

    # Sum all drugs in classification 396 for each prefecture
    prefecture_counts = []

    for col in prefecture_cols:
        # Skip '総計' (total) column
        if '総計' in str(col) or 'Total' in str(col):
            continue

        # Extract prefecture code (should be 2 digits like '01', '13', etc.)
        col_str = str(col)

        # Try to parse as prefecture code
        try:
            # The column header row 3 contains prefecture names
            # We need to get the prefecture code from the column position
            col_idx = df.columns.get_loc(col)

            # Sum all prescriptions for this prefecture (all drugs in class 396)
            total_count = df_filtered[col].sum()

            # Convert to numeric, replacing '-' with 0
            if pd.isna(total_count):
                total_count = 0
            elif isinstance(total_count, str):
                total_count = 0

            prefecture_counts.append({
                'prefecture_code': col_str,
                'prescription_count': total_count
            })

        except Exception as e:
            logger.debug(f'Skipping column {col}: {e}')
            continue

    df_result = pd.DataFrame(prefecture_counts)

    logger.info(f'Extracted {len(df_result)} prefectures')

    return df_result


def merge_prescription_data(df_list: list, file_labels: list) -> pd.DataFrame:
    """
    Merge multiple prescription DataFrames (oral outpatient, inpatient, injection).

    Args:
        df_list: List of DataFrames from different prescription files
        file_labels: List of labels for each DataFrame

    Returns:
        Merged DataFrame with total prescription counts by prefecture
    """
    logger.info('Merging prescription data from multiple files')

    # Start with first DataFrame
    df_merged = df_list[0].copy()
    df_merged = df_merged.rename(columns={'prescription_count': file_labels[0]})

    # Merge remaining DataFrames
    for i in range(1, len(df_list)):
        df = df_list[i].copy()
        df = df.rename(columns={'prescription_count': file_labels[i]})

        df_merged = pd.merge(
            df_merged,
            df[['prefecture_code', file_labels[i]]],
            on='prefecture_code',
            how='outer'
        )

    # Fill NaN with 0
    for label in file_labels:
        df_merged[label] = df_merged[label].fillna(0)

    # Calculate total prescription count
    df_merged['total_prescription'] = df_merged[file_labels].sum(axis=1)

    logger.info(f'Merged data shape: {df_merged.shape}')
    logger.info(f'Total prescription range: {df_merged["total_prescription"].min():.0f} - {df_merged["total_prescription"].max():.0f}')

    return df_merged


def add_prefecture_names_and_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add prefecture names and population data.

    Args:
        df: DataFrame with prefecture_code

    Returns:
        DataFrame with prefecture_name and population columns
    """
    logger.info('Adding prefecture names and population data')

    # Prefecture code to name mapping (01=北海道, ..., 47=沖縄県)
    prefecture_mapping = {
        '01': '北海道', '02': '青森県', '03': '岩手県', '04': '宮城県', '05': '秋田県',
        '06': '山形県', '07': '福島県', '08': '茨城県', '09': '栃木県', '10': '群馬県',
        '11': '埼玉県', '12': '千葉県', '13': '東京都', '14': '神奈川県', '15': '新潟県',
        '16': '富山県', '17': '石川県', '18': '福井県', '19': '山梨県', '20': '長野県',
        '21': '岐阜県', '22': '静岡県', '23': '愛知県', '24': '三重県', '25': '滋賀県',
        '26': '京都府', '27': '大阪府', '28': '兵庫県', '29': '奈良県', '30': '和歌山県',
        '31': '鳥取県', '32': '島根県', '33': '岡山県', '34': '広島県', '35': '山口県',
        '36': '徳島県', '37': '香川県', '38': '愛媛県', '39': '高知県', '40': '福岡県',
        '41': '佐賀県', '42': '長崎県', '43': '熊本県', '44': '大分県', '45': '宮崎県',
        '46': '鹿児島県', '47': '沖縄県'
    }

    # Map prefecture codes to names
    df['prefecture_name'] = df['prefecture_code'].astype(str).str.zfill(2).map(prefecture_mapping)

    # Map prefecture names to population (in thousands)
    df['population_1000'] = df['prefecture_name'].map(PREFECTURE_POPULATION_2022)

    # Remove rows without valid prefecture names
    df = df[df['prefecture_name'].notna()].reset_index(drop=True)

    # Calculate per 100,000 population
    df['prescription_per_100k'] = (df['total_prescription'] / df['population_1000']) * 100

    logger.info(f'Added names and population for {len(df)} prefectures')

    return df


def main():
    """Main execution function."""
    logger.info('=' * 80)
    logger.info('Phase 3: Diabetes Medication Data Extraction')
    logger.info('=' * 80)

    # Load configuration
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    config_path = project_dir / 'config' / 'config.yaml'
    config = load_config(str(config_path))
    logger.info(f'Loaded configuration from: {config_path}')

    # Get drug classification and file names from config
    drug_class = config['outcome_variables']['diabetes_medication']['drug_classification']
    file_names = config['outcome_variables']['diabetes_medication']['file_names']

    logger.info(f'Drug classification: {drug_class} (糖尿病用剤)')
    logger.info(f'Input files: {len(file_names)} files')

    # Define paths
    project_root = Path(__file__).resolve().parents[3]
    prescription_dir = project_root / config['input_paths']['prescription']
    output_dir = project_root / config['output_paths']['interim']
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f'Prescription data dir: {prescription_dir}')
    logger.info(f'Output dir: {output_dir}')

    # Load prescription data from 4 files
    logger.info('-' * 80)
    logger.info('Loading prescription files')
    logger.info('-' * 80)

    df_list = []
    file_labels = ['oral_outpatient_external', 'oral_outpatient_internal', 'oral_inpatient', 'injection']

    for label, file_name in zip(file_labels, file_names.values()):
        file_path = prescription_dir / file_name

        if not file_path.exists():
            logger.error(f'File not found: {file_path}')
            raise FileNotFoundError(f'File not found: {file_path}')

        df = load_prescription_file(file_path, drug_class=drug_class)
        df_list.append(df)

        logger.info(f'{label}: {len(df)} prefectures, total={df["prescription_count"].sum():.0f}')

    # Merge prescription data
    logger.info('-' * 80)
    logger.info('Merging prescription data')
    logger.info('-' * 80)

    df_merged = merge_prescription_data(df_list, file_labels)

    # Add prefecture names and population
    df_result = add_prefecture_names_and_population(df_merged)

    # Display summary statistics
    logger.info('-' * 80)
    logger.info('Summary Statistics')
    logger.info('-' * 80)
    logger.info(f'Total prefectures: {len(df_result)}')
    logger.info(f'\nTotal prescription count:')
    logger.info(f'  Mean: {df_result["total_prescription"].mean():.0f}')
    logger.info(f'  Min:  {df_result["total_prescription"].min():.0f}')
    logger.info(f'  Max:  {df_result["total_prescription"].max():.0f}')
    logger.info(f'\nPrescription per 100,000 population:')
    logger.info(f'  Mean: {df_result["prescription_per_100k"].mean():.0f}')
    logger.info(f'  Min:  {df_result["prescription_per_100k"].min():.0f}')
    logger.info(f'  Max:  {df_result["prescription_per_100k"].max():.0f}')

    # Top 5 highest/lowest prescription rates
    logger.info(f'\nTop 5 highest prescription rates (per 100k):')
    for _, row in df_result.nlargest(5, 'prescription_per_100k').iterrows():
        logger.info(f'  {row["prefecture_name"]}: {row["prescription_per_100k"]:.0f}')

    logger.info(f'\nTop 5 lowest prescription rates (per 100k):')
    for _, row in df_result.nsmallest(5, 'prescription_per_100k').iterrows():
        logger.info(f'  {row["prefecture_name"]}: {row["prescription_per_100k"]:.0f}')

    # Select output columns
    df_output = df_result[[
        'prefecture_code', 'prefecture_name', 'total_prescription',
        'population_1000', 'prescription_per_100k'
    ]].copy()

    # Save output
    output_file = output_dir / 'diabetes_prescription.csv'
    df_output.to_csv(output_file, index=False, encoding='utf-8')
    logger.info('-' * 80)
    logger.info(f'Output saved to: {output_file}')
    logger.info(f'Shape: {df_output.shape}')
    logger.info('-' * 80)

    logger.info('=' * 80)
    logger.info('Phase 3 completed successfully!')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
