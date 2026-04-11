"""
PythonコードブロックからMarkdownテーブルを生成
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
import sys

# UTF-8出力を強制
sys.stdout.reconfigure(encoding='utf-8')

# データファイルのパス
data_path = Path(__file__).parent.parent / "data" / "interim" / "analysis_dataset.csv"
df = pd.read_csv(data_path, dtype={"prefecture_code": str})

# ================
# Table 1: Descriptive Statistics
# ================
print("# Table 1: Descriptive Statistics\n")

vars_def = [
    ("PM25_Mean", "PM2.5 concentration", "μg/m³"),
    ("HbA1c_Mean", "Mean HbA1c", "%"),
    ("Diabetes_Prescription_Per100k", "Diabetes medication prescriptions", "per 100,000"),
    ("Aging_Rate", "Aging rate (≥65 years)", "%"),
    ("Obesity_Rate", "Obesity rate (BMI ≥25)", "%"),
    ("Exercise_Rate", "Exercise habit rate", "%"),
    ("GDP_Per_Capita", "GDP per capita", "10,000 JPY"),
    ("PM25_N_Stations", "PM2.5 monitoring stations", "count"),
]

rows = []
for col, label, unit in vars_def:
    x = df[col].dropna()
    rows.append({
        "Variable": label,
        "Unit": unit,
        "N": int(x.shape[0]),
        "Mean": float(x.mean()),
        "SD": float(x.std(ddof=1)),
        "Min": float(x.min()),
        "Median": float(x.median()),
        "Max": float(x.max()),
    })

table1 = pd.DataFrame(rows)
for c in ["Mean", "SD", "Min", "Median", "Max"]:
    table1[c] = table1[c].round(3)

# Markdownテーブルとして出力
print("| Variable | Unit | N | Mean | SD | Min | Median | Max |")
print("|---|---|---|---|---|---|---|---|")
for _, row in table1.iterrows():
    print(f"| {row['Variable']} | {row['Unit']} | {row['N']} | {row['Mean']} | {row['SD']} | {row['Min']} | {row['Median']} | {row['Max']} |")

print("\n---\n")

# ================
# Table 2: Multivariable OLS Regression Results
# ================
print("# Table 2: Multivariable OLS Regression Results\n")

predictors = ["PM25_Mean", "Aging_Rate", "Obesity_Rate", "Exercise_Rate", "GDP_Per_Capita"]

def fit_table(y_col: str, label: str) -> pd.DataFrame:
    d = df[[y_col] + predictors].dropna().copy()
    X = sm.add_constant(d[predictors])
    y = d[y_col]
    res = sm.OLS(y, X).fit()

    out = pd.DataFrame({
        "Variable": ["PM2.5 (per 1 μg/m³)"] + predictors[1:],
        "β": [res.params["PM25_Mean"]] + [res.params[v] for v in predictors[1:]],
        "SE": [res.bse["PM25_Mean"]] + [res.bse[v] for v in predictors[1:]],
        "p": [res.pvalues["PM25_Mean"]] + [res.pvalues[v] for v in predictors[1:]],
        "95% CI (lower)": [res.conf_int().loc["PM25_Mean", 0]] + [res.conf_int().loc[v, 0] for v in predictors[1:]],
        "95% CI (upper)": [res.conf_int().loc["PM25_Mean", 1]] + [res.conf_int().loc[v, 1] for v in predictors[1:]],
    })
    out.insert(0, "Outcome", label)
    return out

tab_hba1c = fit_table("HbA1c_Mean", "Mean HbA1c (%)")
tab_rx = fit_table("Diabetes_Prescription_Per100k", "Diabetes medication prescriptions per 100,000")

table2 = pd.concat([tab_hba1c, tab_rx], ignore_index=True)

for c in ["β", "SE", "95% CI (lower)", "95% CI (upper)"]:
    table2[c] = table2[c].astype(float).round(6)
table2["p"] = table2["p"].astype(float).map(lambda x: f"{x:.4g}")

# Markdownテーブルとして出力
print("| Outcome | Variable | β | SE | p | 95% CI (lower) | 95% CI (upper) |")
print("|---|---|---|---|---|---|---|")
for _, row in table2.iterrows():
    print(f"| {row['Outcome']} | {row['Variable']} | {row['β']} | {row['SE']} | {row['p']} | {row['95% CI (lower)']} | {row['95% CI (upper)']} |")

print("\n---\n")

# ================
# Table 3: Sensitivity Analyses
# ================
print("# Table 3: Sensitivity Analyses (PM2.5 coefficient)\n")

# 手動データ（原稿から）
rows = [
    # HbA1c
    {"Outcome": "Mean HbA1c (%)", "Analysis": "Main model", "N": 47, "PM2.5 β": 0.003711, "p": 0.4872},
    {"Outcome": "Mean HbA1c (%)", "Analysis": "Stations ≥10", "N": 40, "PM2.5 β": 0.003112, "p": 0.5458},
    {"Outcome": "Mean HbA1c (%)", "Analysis": "Cook's outliers excluded", "N": 43, "PM2.5 β": 0.004674, "p": 0.3147},
    {"Outcome": "Mean HbA1c (%)", "Analysis": "Urban stratum", "N": 23, "PM2.5 β": -0.010077, "p": 0.2488},
    {"Outcome": "Mean HbA1c (%)", "Analysis": "Rural stratum", "N": 24, "PM2.5 β": 0.010749, "p": 0.1166},
    # Prescriptions
    {"Outcome": "Prescriptions per 100,000", "Analysis": "Main model", "N": 47, "PM2.5 β": 6884.110114, "p": 0.7190},
    {"Outcome": "Prescriptions per 100,000", "Analysis": "Stations ≥10", "N": 40, "PM2.5 β": 3963.038374, "p": 0.8429},
    {"Outcome": "Prescriptions per 100,000", "Analysis": "Cook's outliers excluded", "N": 42, "PM2.5 β": 13900.572588, "p": 0.4561},
    {"Outcome": "Prescriptions per 100,000", "Analysis": "Urban stratum", "N": 23, "PM2.5 β": 3277.942160, "p": 0.9159},
    {"Outcome": "Prescriptions per 100,000", "Analysis": "Rural stratum", "N": 24, "PM2.5 β": 34051.959148, "p": 0.2375},
]

table3 = pd.DataFrame(rows)
table3["PM2.5 β"] = table3["PM2.5 β"].round(6)
table3["p"] = table3["p"].map(lambda x: f"{x:.4g}")

# Markdownテーブルとして出力
print("| Outcome | Analysis | N | PM2.5 β | p |")
print("|---|---|---|---|---|")
for _, row in table3.iterrows():
    print(f"| {row['Outcome']} | {row['Analysis']} | {row['N']} | {row['PM2.5 β']} | {row['p']} |")

print("\n完了！")
