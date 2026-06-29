# Reproduction Guide / 再現手順書

This document describes how to reproduce the analyses in:

> Saito H, Ohira T. *Ecological Detectability Boundaries in Nationwide Administrative Data: Lessons from a PM2.5-Diabetes Case Study in Japan.* Public Health. 2026 (under review).

---

## Option A — Minimal reproduction (no raw data download) / 最小再現（生データ不要）

The aggregated prefecture-level dataset (`data/release/analysis_dataset_prefecture_n47.csv`) is
included in this repository. You can reproduce all regression and sensitivity analyses directly:

集計済みデータ（N=47 都道府県）はリポジトリに含まれています。NDB 生データのダウンロードなしに、回帰・感度分析を再現できます。

```bash
git clone https://github.com/haruki00430/ndb-pm25-diabetes-japan.git
cd ndb-pm25-diabetes-japan

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Regression analysis (main results / 主要結果)
python analysis/06_regression_analysis.py

# Sensitivity analyses / 感度分析
python analysis/06c_sensitivity_analysis.py

# Power analysis / 検定力分析
python analysis/06d_power_analysis.py

# Final report / 最終レポート
python analysis/07_final_report.py
```

---

## Option B — Full pipeline (with raw data) / フルパイプライン（生データあり）

Full reproduction requires downloading:
- NDB Open Data 10th edition (No.10) from the Ministry of Health, Labour and Welfare
- Atmospheric PM2.5 monitoring data from the National Institute for Environmental Studies

See **[DATA_SOURCES.md](DATA_SOURCES.md)** for download instructions.

### Step 1 — Place raw data / 生データの配置

```
02_Data/raw/
├── Air_Pollution/
│   ├── TD20221200.zip       # PM2.5 FY2022 (NIES)
│   └── TD20231200.zip       # PM2.5 FY2023 (NIES)
└── NDB_OpenData/No.10/
    ├── 05_処方薬/...          # Prescription data
    └── 07_特定健診 検査/...   # HbA1c examination data
```

### Step 2 — Run pipeline / パイプライン実行

```bash
# Extract PM2.5 data / PM2.5 抽出
python analysis/01_extract_pm25.py

# Extract HbA1c data / HbA1c 抽出
python analysis/02_extract_hba1c.py

# Extract diabetes prescription data / 糖尿病処方薬抽出
python analysis/03_extract_diabetes_prescription.py

# Integrate datasets / データ統合
python analysis/04_integrate_data.py

# Descriptive statistics / 記述統計
python analysis/05_descriptive_statistics.py

# Regression analysis / 回帰分析
python analysis/06_regression_analysis.py
python analysis/06b_regression_reduced_model.py
python analysis/06c_sensitivity_analysis.py
python analysis/06d_power_analysis.py

# Final report / 最終レポート
python analysis/07_final_report.py
```

---

## Expected outputs / 期待される出力

| Script | Key output | Expected result |
|--------|-----------|-----------------|
| `06_regression_analysis.py` | `results/reports/regression_results_ols.txt` | PM2.5 β ≈ 0.00371 for HbA1c, β ≈ 6884 for prescriptions |
| `06c_sensitivity_analysis.py` | `results/reports/sensitivity_analysis.txt` | Null associations across 6 specifications |
| `06d_power_analysis.py` | `results/reports/power_analysis.txt` | Low power to detect small effects at N=47 |

---

## Environment / 実行環境

Analyses were developed and tested on:
- Python 3.10+
- Windows 11 (also compatible with macOS/Linux)
- See `requirements.txt` for package versions

Random seed: 42 (set in `config/config.yaml`)

---

## Notes / 注意事項

- Raw NDB data are not included in this repository (individual-level records are prohibited).
  Only the derived prefecture-level aggregated dataset (`data/release/`) is shared.
- The `scripts/` folder contains manuscript preparation utilities (not required for analysis reproduction).
- For questions, contact: m211039@fmu.ac.jp

- 生の NDB データはリポジトリに含まれていません（個票データの共有は利用規約上禁止）。
  都道府県別集計データ（`data/release/`）のみ公開しています。
