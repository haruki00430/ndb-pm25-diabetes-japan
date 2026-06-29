# Data Sources / データ取得先

Data used in this study are all publicly available. This document describes how to download each source.

本研究で使用したデータはすべて公開データです。各データの取得方法を説明します。

---

## 1. PM2.5 Atmospheric Monitoring Data / 大気中 PM2.5 データ

**Provider / 提供機関:** National Institute for Environmental Studies (NIES) / 国立環境研究所  
**System / システム:** Atmospheric Environmental Regional Observation System (SORAMAME) / そらまめ君  
**Download URL:** https://tenbou.nies.go.jp/download/

### Files required / 必要ファイル

| File | Year | Substance code |
|------|------|---------------|
| `TD20221200.zip` | FY2022 | 1200 (PM2.5) |
| `TD20231200.zip` | FY2023 | 1200 (PM2.5) |

### Download steps / ダウンロード手順

1. Access https://tenbou.nies.go.jp/download/
2. Select: 年別データダウンロード → 物質コード: 1200（PM2.5）→ 年度: 2022, 2023
3. Place downloaded ZIP files in `02_Data/raw/Air_Pollution/`

---

## 2. NDB Open Data (10th Edition, No.10) / NDB オープンデータ第 10 回

**Provider / 提供機関:** Ministry of Health, Labour and Welfare / 厚生労働省  
**Download URL:** https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

### Files required / 必要ファイル

| Category | File | Variable |
|----------|------|---------|
| 特定健診 検査 | HbA1c 都道府県別性年齢階級別分布.xlsx | HbA1c mean (FY2022) |
| 特定健診 質問票 | BMI 都道府県別性年齢階級別分布.xlsx | Obesity rate |
| 特定健診 質問票 | 標準的な質問票（質問項目13）.xlsx | Smoking rate |
| 特定健診 質問票 | 標準的な質問票（質問項目3）.xlsx | Exercise habit |
| 処方薬（内服） | 【内服】外来（院外）都道府県別薬効分類別数量.xlsx | DM prescriptions (FY2023) |
| 処方薬（内服） | 【内服】外来（院内）都道府県別薬効分類別数量.xlsx | (same) |
| 処方薬（内服） | 【内服】入院 都道府県別薬効分類別数量.xlsx | (same) |
| 処方薬（注射） | 【注射】都道府県別薬効分類別数量.xlsx | (same) |

Drug classification / 薬効分類コード: **396** (糖尿病用剤 / antidiabetic drugs)

### Download steps / ダウンロード手順

1. Access the NDB Open Data page
2. Download No.10 (第10回) data package
3. Extract under `02_Data/raw/NDB_OpenData/No.10/`

---

## 3. Population and Aging Rate / 人口・高齢化率

**Provider / 提供機関:** Statistics Bureau, Ministry of Internal Affairs and Communications / 総務省統計局  
**Portal:** e-Stat — https://www.e-stat.go.jp/  
**Dataset:** 人口推計（2022年10月1日現在） / Population Estimates (as of October 1, 2022)

Place data in `02_Data/master/` and update paths in `config/config.yaml`.

---

## 4. GDP per Capita (Prefectural Income) / 1人あたり県民所得

**Provider / 提供機関:** Cabinet Office / 内閣府  
**URL:** https://www.esri.cao.go.jp/jp/sna/data/data_list/kenmin/  
**Dataset:** 県民経済計算（FY2022）/ Prefectural Accounts (FY2022)

---

## Pre-processed aggregated data / 処理済み集計データ

The file `data/release/analysis_dataset_prefecture_n47.csv` contains the fully processed
prefecture-level dataset (N = 47) ready for analysis. No raw NDB data download is required
to reproduce the regression and sensitivity analyses.

`data/release/analysis_dataset_prefecture_n47.csv` には処理済みの都道府県別集計データ（N=47）が
収録されており、回帰・感度分析の再現にはこのファイルのみで十分です（NDB 生データ不要）。

See `data/release/README.md` for the column dictionary.
