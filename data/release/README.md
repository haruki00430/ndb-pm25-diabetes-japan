# data/release — Column Dictionary / カラム辞書

## File / ファイル

`analysis_dataset_prefecture_n47.csv` — Prefecture-level aggregated analytical dataset (N = 47)

都道府県別集計データ（N = 47、市区町村レベルの個人情報は含まれない）

---

## Column Dictionary / カラム一覧

| Column | Type | Unit | Description (EN) | 説明 (JP) |
|--------|------|------|-------------------|-----------|
| `prefecture_code` | str | — | JIS prefecture code (01–47) | 都道府県コード（01–47） |
| `prefecture_name` | str | — | Prefecture name in Japanese | 都道府県名 |
| `PM25_Mean` | float | µg/m³ | Annual mean PM2.5 concentration (FY2022–FY2023 average, monitoring-station mean within prefecture) | PM2.5 年平均濃度（FY2022–FY2023 平均、都道府県内測定局平均） |
| `HbA1c_Mean` | float | % | Age–sex standardised mean HbA1c among specific health check participants (FY2022) | 特定健診受診者の性年齢標準化 HbA1c 平均値（FY2022） |
| `Diabetes_Prescription_Per100k` | float | count / 100 k population | Annual antidiabetic drug prescriptions per 100,000 population (FY2023; drug code 396, inpatient + outpatient combined) | 人口 10 万人あたり糖尿病用剤処方数（FY2023；薬効コード 396、入院＋外来合算） |
| `Aging_Rate` | float | % | Proportion of population aged ≥ 65 years (2022 population estimates) | 65 歳以上人口割合（2022 年 10 月 1 日時点） |
| `Obesity_Rate` | float | % | Proportion with BMI ≥ 25 kg/m² among specific health check participants (FY2022) | 特定健診受診者のBMI ≥ 25 kg/m² 割合（FY2022） |
| `Smoking_Rate` | float | % | Current smoking rate among specific health check participants (questionnaire Q13; FY2022) | 特定健診受診者の現在喫煙率（質問票 Q13；FY2022） |
| `Exercise_Rate` | float | % | Proportion with regular exercise habit (questionnaire Q3; FY2022) | 特定健診受診者の定期的な運動習慣割合（質問票 Q3；FY2022） |
| `GDP_Per_Capita` | float | 万円 | Prefectural income per capita (Cabinet Office FY2022 prefectural accounts; in 万円) | 1 人あたり県民所得（内閣府 FY2022 県民経済計算；単位：万円） |
| `PM25_N_Stations` | int | count | Number of active PM2.5 monitoring stations in the prefecture contributing to `PM25_Mean` | `PM25_Mean` 算出に使用した都道府県内測定局数 |
| `HbA1c_Sample_Size` | float | count | Number of specific health check participants with valid HbA1c measurements (FY2022) | HbA1c 有効測定値がある特定健診受診者数（FY2022） |

---

## Data sources / データ出典

| Variable | Source | Fiscal year |
|----------|--------|-------------|
| PM25_Mean | NIES SORAMAME atmospheric monitoring | FY2022–2023 |
| HbA1c_Mean | NDB Open Data No.10 (特定健診 検査) | FY2022 |
| Diabetes_Prescription_Per100k | NDB Open Data No.10 (処方薬 薬効コード 396) | FY2023 |
| Aging_Rate | Statistics Bureau (e-Stat population estimates) | 2022 |
| Obesity_Rate, Smoking_Rate, Exercise_Rate | NDB Open Data No.10 (特定健診 質問票) | FY2022 |
| GDP_Per_Capita | Cabinet Office (prefectural accounts) | FY2022 |

---

## Notes / 注記

- This file contains **prefectural aggregates only**. No individual-level data are present.
- Preprocessing scripts: `analysis/01_extract_pm25.py` through `analysis/04_integrate_data.py`
- For column derivation details, see `DATA_SOURCES.md` and `REPRODUCE.md`

このファイルは**都道府県別集計値のみ**を含みます。個人を特定できる情報は含まれていません。
