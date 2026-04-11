# Phase 7: 最終サマリーレポート（自動生成）

- 生成日時: 2026-03-12T15:36:24
- 対象: NDB_XXX_PM25_diabetes
- サンプル: 47 都道府県

## 主要結論

- PM2.5 と糖尿病指標（HbA1c平均値、糖尿病用剤処方数/10万人）の関連は、共変量調整後も有意な関連を示さなかった（本データ・本設計の範囲）。
- 多重共線性（共変量間の強相関）が残存しており、係数推定の不安定性・Type II error（偽陰性）の可能性はLimitationsとして明確化が必要。

## 回帰結果（Phase 7で再推定：縮約モデル整合）

### Model 1 (HbA1c)
- 従属変数: `HbA1c_Mean`
- 説明変数: `PM25_Mean, Aging_Rate, Obesity_Rate, Exercise_Rate, GDP_Per_Capita`
- PM2.5係数（β±SE）: 0.00371141 ± 0.00529337（p=0.4872）
- R² / Adj.R²: 0.288 / 0.201
- 残差正規性（Shapiro-Wilk）: W=0.9564, p=0.07759

### Model 2 (Diabetes medication)
- 従属変数: `Diabetes_Prescription_Per100k`
- 説明変数: `PM25_Mean, Aging_Rate, Obesity_Rate, Exercise_Rate, GDP_Per_Capita`
- PM2.5係数（β±SE）: 6884.11 ± 19000.5（p=0.719）
- R² / Adj.R²: 0.291 / 0.204
- 残差正規性（Shapiro-Wilk）: W=0.9932, p=0.9942

## 生成ファイル

- scatter_pm25_hba1c: `C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub/projects/NDB_XXX_PM25_diabetes/results/figures/scatter_pm25_hba1c.png`
- scatter_pm25_dm_rx: `C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub/projects/NDB_XXX_PM25_diabetes/results/figures/scatter_pm25_dm_rx.png`
- diagnostics_hba1c: `C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub/projects/NDB_XXX_PM25_diabetes/results/figures/diagnostics_hba1c.png`
- diagnostics_dm_rx: `C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub/projects/NDB_XXX_PM25_diabetes/results/figures/diagnostics_dm_rx.png`
- stations_by_prefecture: `C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub/projects/NDB_XXX_PM25_diabetes/results/figures/stations_by_prefecture.png`
- table1_top_bottom: `C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub/projects/NDB_XXX_PM25_diabetes/results/reports/table1_top_bottom.csv`
- model_inputs: `C:/Users/user/.ag-cursor-common/research_workspace/projects/NDB_Research_Hub/projects/NDB_XXX_PM25_diabetes/results/reports/model_inputs.csv`

## Choropleth について

- GeoJSON または GeoPandas が利用できないため、choropleth はスキップしました。
- `02_Data/master/japan_prefectures.geojson` を配置すると自動生成されます。
