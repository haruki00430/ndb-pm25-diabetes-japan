> **Repository:** https://github.com/haruki00430/ndb-pm25-diabetes-japan  
> **Reproduction:** [`REPRODUCE.md`](REPRODUCE.md) · [`DATA_SOURCES.md`](DATA_SOURCES.md) · [`analysis/README.md`](analysis/README.md) · [`CITATION.cff`](CITATION.cff)

# Ecological Detectability Boundaries in Nationwide Administrative Data

## Lessons from a PM2.5-Diabetes Case Study in Japan

**論文タイトル（日本語）**: 全国行政データにおける生態学的検出可能性の境界——日本における PM2.5 と糖尿病指標を事例として

**Manuscript status:** Under review at *Public Health* (Elsevier / Royal Society for Public Health), submitted 2026-06-29  
**Repository:** https://github.com/haruki00430/ndb-pm25-diabetes-japan  
**Zenodo DOI:** *(will be assigned after GitHub release — see below)*

---

## Abstract / 研究概要

Established environmental risks may become statistically undetectable when studied with aggregated administrative data. Using the association between ambient PM2.5 and diabetes-related indicators across Japan's 47 prefectures as an empirical case, this study introduces and operationalises the concept of an **ecological detectability boundary**: a confluence of six co-occurring characteristics—narrow exposure contrast, spatial aggregation, outcome aggregation, exposure measurement error, multicollinearity among confounders, and a small sample of *N* = 47 geographic units—that can jointly suppress a meaningful signal below the threshold of statistical detection.

PM2.5 was not significantly associated with prefecture-level mean haemoglobin A1c (β = 0.00371; *p* = 0.487) or diabetes medication prescriptions per 100,000 population (β = 6,884; *p* = 0.719). These null findings persisted across six sensitivity analyses. We propose the detectability boundary as a **design-level diagnostic** for ecological analyses using administrative data.

---

環境リスクは、行政集計データを用いて研究された場合、統計的に検出不可能となることがある。本研究は、日本47都道府県における大気中 PM2.5 濃度と糖尿病関連指標（HbA1c 平均値・糖尿病用剤処方数）の関連を検討し、有意な関連を認めなかった（HbA1c: β = 0.00371, *p* = 0.487; 処方数: β = 6,884, *p* = 0.719）。六つの感度分析でも結果は頑健であった。この帰無所見を「生態学的検出可能性の境界（ecological detectability boundary）」という概念的枠組みから解釈し、行政データを用いた生態学的研究のデザイン段階での診断ツールとして提案する。

---

## Repository structure / リポジトリ構造

```
ndb-pm25-diabetes-japan/
├── analysis/                  # Analysis scripts (01–07) / 解析スクリプト
│   ├── README.md              # Script guide / スクリプト解説
│   ├── 01_extract_pm25.py     # PM2.5 data extraction
│   ├── 02_extract_hba1c.py    # HbA1c data extraction
│   ├── 03_extract_diabetes_prescription.py
│   ├── 04_integrate_data.py   # Data integration
│   ├── 05_descriptive_statistics.py
│   ├── 06_regression_analysis.py
│   ├── 06b_regression_reduced_model.py
│   ├── 06c_sensitivity_analysis.py
│   ├── 06d_power_analysis.py
│   └── 07_final_report.py
├── config/
│   └── config.yaml            # Project settings / プロジェクト設定
├── data/
│   └── release/               # Public aggregated data (N = 47) / 公開集計データ
│       ├── analysis_dataset_prefecture_n47.csv
│       └── README.md          # Column dictionary / 変数辞書
├── results/
│   └── figures/               # Output figures (PNG, 300 dpi)
├── 04_Manuscripts/
│   └── submission_package_RSPH/   # Submission files / 投稿ファイル一式
├── REPRODUCE.md               # Reproduction guide / 再現手順書
├── DATA_SOURCES.md            # Data download instructions / データ取得先
├── CITATION.cff               # Machine-readable citation
├── LICENSE                    # MIT (code)
├── LICENSE-DATA               # CC BY 4.0 (data/release/)
└── requirements.txt           # Python dependencies
```

---

## Quick start / クイックスタート

```bash
git clone https://github.com/haruki00430/ndb-pm25-diabetes-japan.git
cd ndb-pm25-diabetes-japan

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Minimal reproduction (no NDB download required) / 最小再現（NDBダウンロード不要）

```bash
# Uses data/release/analysis_dataset_prefecture_n47.csv
python analysis/06_regression_analysis.py
python analysis/06c_sensitivity_analysis.py
python analysis/07_final_report.py
```

For full pipeline instructions, see **[REPRODUCE.md](REPRODUCE.md)**.

---

## Data sources / データソース

| Source | Description | URL |
|--------|-------------|-----|
| NDB Open Data (10th edition) | HbA1c (FY2022), diabetes medication prescriptions (FY2023) | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html |
| NIES Atmospheric Monitoring | Prefecture-level PM2.5 concentrations (FY2022–2023) | https://tenbou.nies.go.jp/download/ |
| e-Stat / 2020 Population Census | Aging rate, population data | https://www.e-stat.go.jp/ |
| Cabinet Office Prefectural Income | GDP per capita FY2022 | https://www.esri.cao.go.jp/jp/sna/data/data_list/kenmin/ |
| NDB Open Data (questionnaire) | BMI obesity rate, smoking rate, exercise habit | (same NDB URL as above) |

See **[DATA_SOURCES.md](DATA_SOURCES.md)** for detailed download instructions.

---

## Key results / 主要結果

| Outcome | β | SE | *p* |
|---------|---|----|-----|
| Mean HbA1c (%) | 0.00371 | 0.00529 | 0.487 |
| Diabetes prescriptions per 100,000 | 6,884 | 19,001 | 0.719 |

Mean PM2.5: 8.55 μg/m³ (SD 1.12); range 6.18–12.7 μg/m³ across 47 prefectures.  
No significant spatial autocorrelation (Global Moran's I not significant).  
Null associations persisted across all six sensitivity analyses.

---

## Conceptual contribution / 概念的貢献

This paper defines and empirically illustrates the **ecological detectability boundary**—a design-level concept identifying when administrative ecological data cannot be expected to detect an established environmental effect. The boundary is characterised by six co-occurring conditions:

1. Narrow exposure contrast (σ = 1.12 μg/m³)
2. Spatial aggregation to prefectural level
3. Outcome aggregation (mean HbA1c; annual prescription counts)
4. Exposure measurement error (sparse monitoring stations)
5. Multicollinearity among socioeconomic confounders
6. Small sample size (*N* = 47)

生態学的検出可能性の境界は、行政データを用いた生態学的研究において、既知の環境的影響を検出することが期待できない条件を事前に評価するための概念的診断ツールである。

---

## Citation / 引用

If you use this code or dataset, please cite:

```
Saito H, Ohira T. Ecological Detectability Boundaries in Nationwide
Administrative Data: Lessons from a PM2.5-Diabetes Case Study in Japan.
Public Health. 2026 (under review).
```

See **[CITATION.cff](CITATION.cff)** for machine-readable metadata.

*(DOI badge will appear here after Zenodo release)*

---

## License / ライセンス

- **Code** (`analysis/`, `config/`): [MIT License](LICENSE)
- **Aggregated data** (`data/release/`): [CC BY 4.0](LICENSE-DATA)

The raw NDB Open Data are available from the Ministry of Health, Labour and Welfare and are subject to their terms of use. No individual-level data are included in this repository.

---

## Authors / 著者

| Name | Affiliation | ORCID |
|------|-------------|-------|
| Haruki Saito (corresponding) | Department of Epidemiology, Fukushima Medical University School of Medicine | [0009-0009-7890-6068](https://orcid.org/0009-0009-7890-6068) |
| Tetsuya Ohira | Radiation Medical Science Center for the Fukushima Health Management Survey, Fukushima Medical University | [0000-0003-4532-7165](https://orcid.org/0000-0003-4532-7165) |
