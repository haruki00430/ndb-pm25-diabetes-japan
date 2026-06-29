# analysis/ — Script Guide / スクリプトガイド

Run scripts in numbered order. Scripts 06–07 can be run using only `data/release/analysis_dataset_prefecture_n47.csv` (no raw data required).

スクリプトは番号順に実行します。06〜07 は `data/release/analysis_dataset_prefecture_n47.csv` のみで実行可能（生データ不要）。

---

## Execution order / 実行順序

### Phase 1 — Data extraction (requires raw data) / データ抽出（生データ必要）

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `01_extract_pm25.py` | `02_Data/raw/Air_Pollution/*.zip` | `data/interim/pm25_prefecture.csv` | Extract prefecture-level annual mean PM2.5 from NIES SORAMAME monitoring data |
| `02_extract_hba1c.py` | `02_Data/raw/NDB_OpenData/No.10/07_特定健診 検査/` | `data/interim/hba1c_prefecture.csv` | Extract age–sex standardised mean HbA1c per prefecture (FY2022) |
| `03_extract_diabetes_prescription.py` | `02_Data/raw/NDB_OpenData/No.10/05_処方薬/` | `data/interim/diabetes_prescription.csv` | Aggregate antidiabetic prescriptions (drug code 396) per 100k population (FY2023) |
| `04_integrate_data.py` | `data/interim/*.csv` + master data | `data/interim/analysis_dataset.csv` | Merge all variables into one prefecture-level analytical dataset (N=47) |

### Phase 2 — Analysis (no raw data required) / 解析（生データ不要）

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `05_descriptive_statistics.py` | `data/interim/analysis_dataset.csv` | `results/reports/descriptive_stats.txt` | Summary statistics, correlation matrix |
| `06_regression_analysis.py` | `data/interim/analysis_dataset.csv` | `results/reports/regression_results_ols_model*.txt` | OLS regression (Model 1: HbA1c; Model 2: prescriptions); VIF, Moran's I |
| `06b_regression_reduced_model.py` | `data/interim/analysis_dataset.csv` | `results/reports/regression_results_ols_model*_reduced.txt` | Reduced-variable OLS (aging rate + obesity rate only as covariates) |
| `06c_sensitivity_analysis.py` | `data/interim/analysis_dataset.csv` | `results/reports/sensitivity_analysis_results.txt` | 6-specification robustness checks (HC3, outlier exclusion, metropolitan exclusion, log transform, additional covariates) |
| `06d_power_analysis.py` | — | `results/reports/power_analysis.txt` | Post-hoc power analysis at N=47 |
| `07_final_report.py` | `results/reports/` | `results/reports/final_report.txt` | Consolidated summary of all analyses |

---

## Quick start (Option A — no raw data) / クイックスタート（生データなし）

```bash
cd ndb-pm25-diabetes-japan

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

python analysis/06_regression_analysis.py
python analysis/06c_sensitivity_analysis.py
python analysis/06d_power_analysis.py
python analysis/07_final_report.py
```

Scripts 06–07 auto-detect whether `data/release/analysis_dataset_prefecture_n47.csv` or `data/interim/analysis_dataset.csv` is available and use whichever is present.

---

## Configuration / 設定

All paths and parameters are managed in `config/config.yaml`. Key settings:

| Key | Default | Description |
|-----|---------|-------------|
| `random_seed` | 42 | Random seed for reproducibility |
| `drug_code` | 396 | NDB drug classification code for antidiabetic drugs |
| `experiment_mode` | false | Add "SAMPLE DATA" watermark to figures when `true` |

---

## Output files / 出力ファイル

```
results/
├── reports/
│   ├── descriptive_stats.txt
│   ├── regression_results_ols_model1.txt      # HbA1c outcome
│   ├── regression_results_ols_model2.txt      # Prescription outcome
│   ├── regression_results_ols_model1_reduced.txt
│   ├── regression_results_ols_model2_reduced.txt
│   ├── vif_results.csv
│   ├── morans_i_model1.txt
│   ├── morans_i_model2.txt
│   ├── sensitivity_analysis_results.txt
│   ├── power_analysis.txt
│   └── final_report.txt
└── figures/
    ├── fig1a_choropleth_pm25.png
    ├── fig1b_scatter_pm25_rx.png
    ├── fig2_choropleth_hba1c.png
    ├── fig3_scatter_pm25_hba1c.png
    └── (supplementary figures)
```

---

## scripts/ folder / scripts/ フォルダについて

The `scripts/` folder contains **manuscript preparation utilities** (citation conversion, DOCX formatting). These are not required for analysis reproduction.

`scripts/` はDOCX整形・引用変換等の投稿補助スクリプトです。解析再現には不要です。
