# Table 1: Descriptive Statistics

| Variable | Unit | N | Mean | SD | Min | Median | Max |
|---|---|---|---|---|---|---|---|
| PM2.5 concentration | μg/m³ | 47 | 8.548 | 1.118 | 6.322 | 8.475 | 11.174 |
| Mean HbA1c | % | 47 | 5.741 | 0.043 | 5.645 | 5.742 | 5.836 |
| Diabetes medication prescriptions | per 100,000 | 47 | 603929.791 | 154635.677 | 157968.869 | 585262.194 | 931960.102 |
| Aging rate (≥65 years) | % | 47 | 31.43 | 3.031 | 22.4 | 31.9 | 38.6 |
| Obesity rate (BMI ≥25) | % | 47 | 26.536 | 1.251 | 23.1 | 26.5 | 30.8 |
| Exercise habit rate | % | 47 | 26.443 | 1.495 | 22.3 | 26.4 | 29.8 |
| GDP per capita | 10,000 JPY | 47 | 309.409 | 53.983 | 232.7 | 301.2 | 623.4 |
| PM2.5 monitoring stations | count | 47 | 23.809 | 20.516 | 4.0 | 16.0 | 86.0 |

---

# Table 2: Multivariable OLS Regression Results

| Outcome | Variable | β | SE | p | 95% CI (lower) | 95% CI (upper) |
|---|---|---|---|---|---|---|
| Mean HbA1c (%) | PM2.5 (per 1 μg/m³) | 0.003711 | 0.005293 | 0.4872 | -0.006979 | 0.014402 |
| Mean HbA1c (%) | Aging_Rate | 0.001017 | 0.002247 | 0.6531 | -0.00352 | 0.005555 |
| Mean HbA1c (%) | Obesity_Rate | 0.026185 | 0.010607 | 0.01782 | 0.004765 | 0.047606 |
| Mean HbA1c (%) | Exercise_Rate | 0.014207 | 0.008308 | 0.09481 | -0.002571 | 0.030985 |
| Mean HbA1c (%) | GDP_Per_Capita | -0.000139 | 0.000151 | 0.3623 | -0.000444 | 0.000166 |
| Diabetes medication prescriptions per 100,000 | PM2.5 (per 1 μg/m³) | 6884.110114 | 19000.474754 | 0.719 | -31488.127109 | 45256.347337 |
| Diabetes medication prescriptions per 100,000 | Aging_Rate | 32080.510738 | 8065.0113 | 0.0002765 | 15792.889991 | 48368.131486 |
| Diabetes medication prescriptions per 100,000 | Obesity_Rate | -8612.167655 | 38072.122741 | 0.8222 | -85500.379363 | 68276.044053 |
| Diabetes medication prescriptions per 100,000 | Exercise_Rate | 9253.127649 | 29820.847396 | 0.7579 | -50971.295441 | 69477.550739 |
| Diabetes medication prescriptions per 100,000 | GDP_Per_Capita | 600.482971 | 541.656061 | 0.2741 | -493.413636 | 1694.379578 |

---

# Table 3: Sensitivity Analyses (PM2.5 coefficient)

| Outcome | Analysis | N | PM2.5 β | p |
|---|---|---|---|---|
| Mean HbA1c (%) | Main model | 47 | 0.003711 | 0.4872 |
| Mean HbA1c (%) | Stations ≥10 | 40 | 0.003112 | 0.5458 |
| Mean HbA1c (%) | Cook's outliers excluded | 43 | 0.004674 | 0.3147 |
| Mean HbA1c (%) | Urban stratum | 23 | -0.010077 | 0.2488 |
| Mean HbA1c (%) | Rural stratum | 24 | 0.010749 | 0.1166 |
| Prescriptions per 100,000 | Main model | 47 | 6884.110114 | 0.719 |
| Prescriptions per 100,000 | Stations ≥10 | 40 | 3963.038374 | 0.8429 |
| Prescriptions per 100,000 | Cook's outliers excluded | 42 | 13900.572588 | 0.4561 |
| Prescriptions per 100,000 | Urban stratum | 23 | 3277.94216 | 0.9159 |
| Prescriptions per 100,000 | Rural stratum | 24 | 34051.959148 | 0.2375 |

完了！
