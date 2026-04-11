# HANDOVER: NDB_XXX_PM25_diabetes プロジェクト引き継ぎ資料

**作成日**: 2026-03-12
**プロジェクト開始日**: 2026-03-12
**現在のステータス**: Phase 6d 完了（統計的検出力分析完了）
**進捗率**: 93% (Phase 7 残り)

---

## 📋 プロジェクト概要

### 研究テーマ
**PM2.5大気汚染曝露と糖尿病指標の都道府県レベル生態学的研究**

### 研究仮説
PM2.5曝露レベルが高い都道府県ほど、糖尿病関連指標（HbA1c平均値、糖尿病処方薬）が高い。

### 研究デザイン
- **デザイン**: 横断的生態学的研究（Cross-sectional ecological study）
- **空間単位**: 日本47都道府県
- **サンプルサイズ**: N=47
- **データソース**:
  1. 環境省SORAMAME（PM2.5測定データ、2022-2023年）
  2. NDB Open Data No.10（特定健診HbA1c、処方薬、2021年度）
  3. 都道府県統計（高齢化率、肥満率、喫煙率、運動習慣率、GDP）

### 主要アウトカム
1. **HbA1c平均値**（特定健診受診者、都道府県別）
2. **糖尿病処方薬数/10万人**（レセプト請求数、都道府県別）

---

## 🎯 実施済みフェーズの詳細

### ✅ Phase 1: PM2.5データ抽出（環境省SORAMAME）

**実施内容**:
- 環境省大気汚染物質広域監視システム（SORAMAME）から2022-2023年のPM2.5データを抽出
- 都道府県別に測定局数、年平均PM2.5濃度を算出

**スクリプト**: `analysis/01_extract_pm25.py`

**出力ファイル**: `data/interim/pm25_by_prefecture.csv`

**主要結果**:
- 測定局総数: 689局
- PM2.5濃度範囲: 6.32-11.17 μg/m³（平均: 8.55 ± 1.12 μg/m³）
- 測定局数のばらつき: 北海道28局 vs 青森5局（6倍の差）

**注意事項**:
- 測定局が都市部に偏在（農村部の曝露を過小評価の可能性）
- 2年間平均では長期曝露を完全には捉えられない

---

### ✅ Phase 2: HbA1cデータ抽出（NDB特定健診）

**実施内容**:
- NDB Open Data No.10「特定健診 検査」から都道府県別HbA1c平均値を抽出
- 全年齢階級・性別統合データを使用

**スクリプト**: `analysis/02_extract_hba1c.py`

**出力ファイル**: `data/interim/hba1c_by_prefecture.csv`

**主要結果**:
- HbA1c平均値範囲: 5.645-5.836%（平均: 5.741 ± 0.043%）
- サンプルサイズ: 総計28,773,966人（都道府県別: 238,403-2,308,279人）

**注意事項**:
- 特定健診受診者のみ（40-74歳、受診率約50%）
- 健康意識の高い層にバイアスの可能性

---

### ✅ Phase 3: 糖尿病処方薬データ抽出（NDB処方薬）

**実施内容**:
- NDB Open Data No.10「処方薬」から糖尿病用剤（内服・注射）を抽出
- 都道府県別処方数を人口10万対に標準化

**スクリプト**: `analysis/03_extract_diabetes_prescription.py`

**出力ファイル**: `data/interim/diabetes_prescription_by_prefecture.csv`

**主要結果**:
- 処方数/10万人範囲: 157,969-931,960（平均: 603,930 ± 154,636）
- 6倍の地域格差（最大: 秋田県、最小: 神奈川県）

**注意事項**:
- レセプト請求数（処方頻度を反映するが、有病率とは異なる）
- 医療アクセス、処方パターンの地域差の影響

---

### ✅ Phase 4: データ統合

**実施内容**:
- Phase 1-3の出力を統合
- 共変量（高齢化率、肥満率、喫煙率、運動習慣率、GDP）を追加

**スクリプト**: `analysis/04_integrate_data.py`

**出力ファイル**: `data/interim/analysis_dataset.csv`

**データセット構造**:
- **行数**: 47都道府県
- **列数**: 12変数
- **欠損値**: なし（すべて完全データ）

**変数リスト**:
1. prefecture_code (都道府県コード)
2. prefecture_name (都道府県名)
3. PM25_Mean (PM2.5平均濃度, μg/m³)
4. HbA1c_Mean (HbA1c平均値, %)
5. Diabetes_Prescription_Per100k (糖尿病処方薬数/10万人)
6. Aging_Rate (高齢化率, %)
7. Obesity_Rate (肥満率, %)
8. Smoking_Rate (喫煙率, %)
9. Exercise_Rate (運動習慣率, %)
10. GDP_Per_Capita (一人当たりGDP, 万円)
11. PM25_N_Stations (PM2.5測定局数)
12. HbA1c_Sample_Size (HbA1cサンプルサイズ)

**重要な修正**:
- prefecture_codeの型不一致エラーを修正（int64 → str, zero-padding）
- defensive copy作成で元データ保護

---

### ✅ Phase 5: 記述統計・EDA

**実施内容**:
- 記述統計量の算出（平均、標準偏差、中央値、IQR、CV）
- Pearson相関行列の計算
- 可視化（ヒストグラム、相関ヒートマップ、散布図行列）

**スクリプト**: `analysis/05_descriptive_statistics.py`

**出力ファイル**:
1. `results/reports/descriptive_statistics.csv`
2. `results/reports/correlation_matrix.csv`
3. `results/figures/histograms.png`
4. `results/figures/correlation_heatmap.png`
5. `results/figures/scatterplot_matrix.png`

**主要な発見**:

#### ⚠️ **重要**: PM2.5との相関がほぼゼロ
- **PM25_Mean ↔ HbA1c_Mean**: r = 0.005（ほぼ無相関）
- **PM25_Mean ↔ Diabetes_Prescription_Per100k**: r = 0.005（ほぼ無相関）

#### 強い多重共線性を検出
- **Obesity_Rate ↔ Smoking_Rate**: r = 0.959 ⚠️
- **Smoking_Rate ↔ Exercise_Rate**: r = -0.904
- **Obesity_Rate ↔ Exercise_Rate**: r = -0.878

これらの強相関は、後のPhase 6でVIF>5000という深刻な多重共線性として顕在化。

---

### ✅ Phase 6: 回帰分析（OLS + 空間統計）

**実施内容**:
1. VIF計算（多重共線性チェック）
2. OLS回帰（2モデル）
3. Moran's I検定（空間的自己相関）
4. 空間回帰モデル（SLM/SEM、必要時のみ）

**スクリプト**: `analysis/06_regression_analysis.py`

**出力ファイル**:
1. `results/reports/vif_results.csv`
2. `results/reports/regression_results_ols_model1.txt`
3. `results/reports/morans_i_model1.txt`
4. `results/reports/regression_results_ols_model2.txt`
5. `results/reports/morans_i_model2.txt`

#### 📊 **VIF結果（多重共線性チェック）**

| 変数 | VIF | 判定 |
|------|-----|------|
| PM25_Mean | 61.29 | 要注意（VIF>=10） |
| Aging_Rate | 153.23 | 要注意（VIF>=10） |
| **Obesity_Rate** | **5956.41** | **極めて深刻** |
| **Smoking_Rate** | **6239.40** | **極めて深刻** |
| Exercise_Rate | 260.70 | 要注意（VIF>=10） |
| GDP_Per_Capita | 59.90 | 要注意（VIF>=10） |

**Condition Number**: 3.29 × 10⁴（基準: <30が望ましい、>10,000で深刻）

**診断**:
- すべての変数でVIF≥10（多重共線性あり）
- Obesity_Rate/Smoking_Rateで極端に高い（r=0.959の結果）
- 回帰係数の標準誤差が過大推定される可能性

---

#### 📊 **Model 1: PM25_Mean → HbA1c_Mean**

**モデル式**:
```
HbA1c_Mean = β₀ + β₁·PM25_Mean + β₂·Aging_Rate + β₃·Obesity_Rate
             + β₄·Smoking_Rate + β₅·Exercise_Rate + β₆·GDP_Per_Capita + ε
```

**モデル適合度**:
- **R²**: 0.3645 (36.5%の分散を説明)
- **Adjusted R²**: 0.2692
- **F-statistic**: 3.82 (p=0.004) → モデル全体は有意

**回帰係数**:

| 変数 | β係数 | 標準誤差 | t値 | p値 | 95%CI |
|------|-------|---------|-----|-----|-------|
| 定数項 | 4.1594 | 0.553 | 7.515 | **<0.001** | [3.041, 5.278] |
| **PM25_Mean** | **0.0027** | 0.005 | 0.524 | **0.603** ❌ | [-0.008, 0.013] |
| Aging_Rate | 0.0002 | 0.002 | 0.114 | 0.909 | [-0.004, 0.005] |
| Obesity_Rate | -0.0012 | 0.016 | -0.072 | 0.943 | [-0.034, 0.031] |
| **Smoking_Rate** | **0.0557** | 0.025 | 2.200 | **0.034** ✅ | [0.005, 0.107] |
| **Exercise_Rate** | **0.0223** | 0.009 | 2.548 | **0.015** ✅ | [0.005, 0.040] |
| GDP_Per_Capita | -0.000079 | 0.000 | -0.540 | 0.592 | [-0.000, 0.000] |

**診断統計**:
- **Shapiro-Wilk** (残差の正規性): W=0.9696, p=0.255 → 正規分布に従う ✅
- **Durbin-Watson**: 2.57 → 自己相関なし ✅
- **Moran's I** (空間的自己相関): I=-0.147, p=0.117 → 空間依存性なし ✅

**結論**:
- **PM2.5はHbA1cと有意な関連なし（p=0.603）** ❌
- Smoking_Rate, Exercise_Rateのみ有意
- 空間回帰モデル（SLM/SEM）は不要（Moran's I非有意）

---

#### 📊 **Model 2: PM25_Mean → Diabetes_Prescription_Per100k**

**モデル式**:
```
Prescription_Per100k = β₀ + β₁·PM25_Mean + β₂·Aging_Rate + β₃·Obesity_Rate
                       + β₄·Smoking_Rate + β₅·Exercise_Rate + β₆·GDP_Per_Capita + ε
```

**モデル適合度**:
- **R²**: 0.2991 (29.9%の分散を説明)
- **Adjusted R²**: 0.1940
- **F-statistic**: 2.85 (p=0.021) → モデル全体は有意

**回帰係数**:

| 変数 | β係数 | 標準誤差 | t値 | p値 | 95%CI |
|------|-------|---------|-----|-----|-------|
| 定数項 | -77,670 | 2.09×10⁶ | -0.037 | 0.971 | [-4.3×10⁶, 4.15×10⁶] |
| **PM25_Mean** | **8138.99** | 1.92×10⁴ | 0.424 | **0.674** ❌ | [-3.07×10⁴, 4.7×10⁴] |
| **Aging_Rate** | **33,000** | 8222.54 | 4.013 | **<0.001** ✅ | [1.64×10⁴, 4.96×10⁴] |
| Obesity_Rate | 24,120 | 6.06×10⁴ | 0.398 | 0.693 | [-9.84×10⁴, 1.47×10⁵] |
| Smoking_Rate | -66,660 | 9.56×10⁴ | -0.697 | 0.490 | [-2.6×10⁵, 1.27×10⁵] |
| Exercise_Rate | -450.96 | 3.31×10⁴ | -0.014 | 0.989 | [-6.73×10⁴, 6.64×10⁴] |
| GDP_Per_Capita | 528.92 | 554.67 | 0.954 | 0.346 | [-592.1, 1649.9] |

**診断統計**:
- **Shapiro-Wilk** (残差の正規性): W=0.9908, p=0.971 → 正規分布に従う ✅
- **Durbin-Watson**: 1.93 → 自己相関なし ✅
- **Moran's I** (空間的自己相関): I=-0.037, p=0.461 → 空間依存性なし ✅

**結論**:
- **PM2.5は糖尿病処方薬と有意な関連なし（p=0.674）** ❌
- Aging_Rateのみが有意（既知の知見）
- 空間回帰モデル（SLM/SEM）は不要（Moran's I非有意）

---




### ✅ Phase 6b: 変数選択の再設計（VIFベース）

**実施内容**:
- VIFベースの逐次削除で共変量を再選択（`config.yaml`で制御）
- Smoking_Rate除外 → Obesity_Rateとの多重共線性（r=0.959）を解消
- 主要曝露（PM25_Mean）は保護し、共変量を最小限まで削減

**スクリプト**: `analysis/06b_regression_reduced_model.py`

**出力ファイル**（実際のファイル名: `*_reduced`）:
1. `results/reports/vif_results_reduced.csv`
2. `results/reports/regression_results_ols_model1_reduced.txt`
3. `results/reports/morans_i_model1_reduced.txt`
4. `results/reports/regression_results_ols_model2_reduced.txt`
5. `results/reports/morans_i_model2_reduced.txt`

**ログ**:
- `analysis/logs/06b_regression_reduced_model.log`

#### 📊 **VIF結果（縮約モデル: Smoking_Rate除外）**

| 変数 | VIF | 判定 |
|------|-----|------|
| PM25_Mean | 57.78 | 要注意（VIF>=10） |
| Aging_Rate | 139.42 | 要注意（VIF>=10） |
| Obesity_Rate | 223.40 | 要注意（VIF>=10） |
| Exercise_Rate | 255.80 | 要注意（VIF>=10） |
| GDP_Per_Capita | 59.89 | 要注意（VIF>=10） |

**評価**: Smoking_Rate除外によりVIFは大幅改善（5956→223）したが、全変数でVIF≥10のまま残存。Condition Number = 3.00×10⁴（依然として深刻）。PCAやRidge回帰による追加対応が望ましい。

#### 📊 **Model 1: PM25_Mean → HbA1c_Mean（縮約モデル）**

- **R²**: 0.288 / **Adj.R²**: 0.201
- **PM25_Mean**: β=0.0037, p=0.487 ❌（非有意）
- **Obesity_Rate**: β=0.0262, p=0.018 ✅（有意）
- **Moran's I**: I=-0.0915, p=0.266 → 空間依存性なし ✅

#### 📊 **Model 2: PM25_Mean → Diabetes_Prescription_Per100k（縮約モデル）**

- **R²**: 0.291 / **Adj.R²**: 0.204
- **PM25_Mean**: β=6884.11, p=0.719 ❌（非有意）
- **Aging_Rate**: β=32,080, p=0.000 ✅（有意）
- **Moran's I**: I=-0.0248, p=0.491 → 空間依存性なし ✅


---

### ✅ Phase 6c: 感度分析（Sensitivity Analysis）

**実施内容**:
1. **SA1**: PM2.5測定局数 ≥ 10 の都道府県に限定（N=40）
2. **SA2**: Cook's distance > 4/N の外れ値除外
3. **SA3**: 都市部 vs 農村部 層別解析（人口密度中央値: 270.7人/km²）

**スクリプト**: `analysis/06c_sensitivity_analysis.py`

**出力ファイル**: `results/reports/sensitivity_analysis_results.txt`

#### 📊 **感度分析 結果サマリー**

##### HbA1c_Mean

| 分析 | N | PM25_β | p値 | 有意 |
|------|---|--------|-----|------|
| メインモデル（全47都道府県） | 47 | 0.003711 | 0.487 | ❌ ns |
| SA1: 測定局 ≥ 10 | 40 | 0.003112 | 0.546 | ❌ ns |
| SA2: Cook's外れ値除外（4都道府県除外）| 43 | 0.004674 | 0.315 | ❌ ns |
| SA3: 都市部 | 23 | -0.010077 | 0.249 | ❌ ns |
| SA3: 農村部 | 24 | 0.010749 | 0.117 | ❌ ns |

##### Diabetes_Prescription_Per100k

| 分析 | N | PM25_β | p値 | 有意 |
|------|---|--------|-----|------|
| メインモデル（全47都道府県） | 47 | 6884.1 | 0.719 | ❌ ns |
| SA1: 測定局 ≥ 10 | 40 | 3963.0 | 0.843 | ❌ ns |
| SA2: Cook's外れ値除外（5都道府県除外）| 42 | 13900.6 | 0.456 | ❌ ns |
| SA3: 都市部 | 23 | 3277.9 | 0.916 | ❌ ns |
| SA3: 農村部 | 24 | 34051.9 | 0.238 | ❌ ns |

**Cook's外れ値（HbA1c）**: 青森県、秋田県、石川県、熊本県
**Cook's外れ値（処方薬）**: 青森県、東京都、長野県、鹿児島県、沖縄県

#### 結論

**いかなる感度分析条件下でも、PM2.5と糖尿病指標の有意な関連は検出されなかった。**
ネガティブ結果は頑健であり、測定局の偏在や外れ値の影響によるものではないと判断できる。






### ✅ Phase 6d: 統計的検出力分析（Post-hoc Power）

**実施内容**:
- 観察されたモデル適合度に基づく検出力評価
- 効果量区分ごとの必要サンプルサイズの確認
- PM2.5単独効果の検出限界の評価

**スクリプト**: `analysis/06d_power_analysis.py`

**出力ファイル**: `results/reports/power_analysis_results.txt`

**結論**:
- モデル全体の検出力は十分だが、PM2.5単独効果の検出には不確実性が残る。

---

## 🔍 主要な発見（Key Findings）

### 1. **主要仮説は棄却** ❌

**PM2.5大気汚染は、糖尿病関連指標と有意な関連を示さなかった。**

- Model 1 (HbA1c): β=0.0027, **p=0.603**
- Model 2 (処方薬): β=8138.99, **p=0.674**

この結果は、Phase 5のEDAで観察されたPearson相関係数 r≈0.005（ほぼゼロ）と一致。

---

### 2. **深刻な多重共線性** 🔴

すべての共変量でVIF≥10を検出：

- **Obesity_Rate vs Smoking_Rate**: VIF>5000（r=0.959）
- **Condition Number**: 3.29×10⁴（基準: <30）

**影響**:
- 回帰係数の標準誤差が過大推定される
- PM2.5の真の効果が隠されている可能性（Type II error）

---

### 3. **サンプルサイズと統計的検出力** ✅

**Phase 6d Post-hoc Power 結果（scipy.stats.ncf による正確な計算）**:
- N=47、独立変数5個
- 観察 R² = 0.288（Model 1）、0.291（Model 2）
- Cohen's f² = 0.404 / 0.410（**large effect**区分）
- **統計的検出力: ≈ 90.3% / 90.7%（十分: ≥ 80%）** ✅

**必要サンプルサイズ（80%検出力）**:
- small効果量（f²=0.02）: N=647（実現不可）
- medium効果量（f²=0.15）: N=92（実現不可）
- large効果量（f²=0.35）: N=43（現在の47で達成）
- 観察効果量（f²≈0.40）: N=38（47で達成済み）

**示唆**:
- モデル全体（R²）に対する検出力は十分
- ただし PM2.5 単独の効果量は極めて小さい（β≈0 から推定）
- PM2.5 の部分的効果に対しては依然として Type II error リスクあり

---

### 4. **曝露評価の問題** ⚠️

**PM2.5測定局の分布**:
- 測定局数: 5-28局/都道府県（6倍の差）
- 都市部偏在: 農村部の曝露を過小評価
- 曝露期間: 2年間平均（長期曝露には不十分）

**示唆**:
- 曝露の測定誤差（differential misclassification）が結果を帰無仮説方向にバイアス

---

### 5. **空間的自己相関は検出されず** ✅

両モデルとも、残差にMoran's I有意な空間的自己相関なし：
- Model 1: I=-0.147, p=0.117
- Model 2: I=-0.037, p=0.461

**示唆**:
- 空間回帰モデル（SLM/SEM）は不要
- OLS回帰で十分（空間依存性の問題なし）

---

## ⚠️ 発見された問題点

### 🔴 Critical Issues（論文化の障壁）

1. **多重共線性が極めて深刻**
   - VIF>5000（Obesity_Rate, Smoking_Rate）
   - Condition Number>30,000
   - 査読者が必ず指摘する致命的問題

2. **主要仮説が両方とも棄却**
   - PM2.5 → HbA1c: p=0.603
   - PM2.5 → 処方薬: p=0.674
   - ネガティブ結果のみでは新規性不足

3. **PM2.5単独効果の検出力に不確実性**
   - モデル全体の検出力は十分だが、部分効果の検出は難しい
   - Type II errorのリスクは残る

4. **曝露評価の妥当性に疑問**
   - 測定局の都市部偏在
   - 2年間平均では長期曝露不十分

---

### 🟡 Moderate Issues（修正可能）

1. **共変量データの出典不明**
   - COVARIATES_DATAが埋め込みコード（再現性に問題）
   - 公的統計（e-Stat等）へのリンク必要

2. **交絡因子の不十分な制御**
   - 食生活（塩分・糖質摂取）未測定
   - 遺伝的要因未考慮
   - 医療アクセス（医療機関密度）未調整

3. **生態学的誤謬のリスク**
   - 都道府県レベルの関連 ≠ 個人レベルの関連
   - 都道府県内の曝露・アウトカムの分散を無視

---

## 📊 査読者視点による論文化可能性評価

### 総合スコア: **45/100** 🔴

| 評価項目 | 配点 | 獲得点 | 評価 |
|---------|------|--------|------|
| 1. 科学的意義 | 20点 | **12点** | 🟡 中程度 |
| 2. 方法論の妥当性 | 25点 | **8点** | 🔴 不十分 |
| 3. 結果の質 | 25点 | **10点** | 🔴 低い |
| 4. 制限事項への対処 | 10点 | **5点** | 🟡 やや不十分 |
| 5. 投稿可能性 | 20点 | **10点** | 🟡 条件付き |
| **合計** | **100点** | **45点** | **🔴 現状では論文化困難** |

---

### ターゲットジャーナル別採択可能性

| ジャーナル | Impact Factor | 採択可能性 | 条件 |
|-----------|---------------|-----------|------|
| Environmental Health Perspectives | 11.0 | **<5%** 🔴 | 多重共線性未解決では不可 |
| Environmental Research | 8.3 | **15-20%** 🟡 | 多重共線性解決 + 感度分析必須 |
| **Journal of Epidemiology** | 2.9 | **40-50%** 🟢 | Discussion強化で可能性あり |
| PLOS ONE | 3.7 | **30-40%** 🟡 | 方法論の詳細記述必須 |

**推奨**: Journal of Epidemiology（日本疫学会誌、ネガティブ結果にも寛容）

---

## 🛠️ 論文化のために必要な追加作業

### 必須作業（Must Do）

#### 1. **Phase 7a: Discussion徹底強化** 🔴

**必須要素**（4000-5000語推奨）:

1. **主要な知見の要約**
   - PM2.5と糖尿病の関連なし（両モデルで非有意）

2. **先行研究との比較**
   - 個人レベル研究（コホート研究）との相違
   - Ecologic studyでの一貫性/非一貫性

3. **なぜ関連が見られなかったか（5つの可能性）**:
   - **生態学的誤謬**: 都道府県レベル ≠ 個人レベル
   - **曝露評価の問題**: 測定局偏在、2年間平均では不十分
   - **多重共線性**: VIF>5000により真の効果が隠された可能性
   - **PM2.5単独効果の検出力の限界**: 部分効果が小さく、Type II errorのリスクが残る
   - **交絡因子**: 食生活、遺伝、医療アクセス未測定

4. **研究の強み（Strengths）**:
   - 公的データ（SORAMAME + NDB）の信頼性
   - 全国47都道府県の網羅的データ
   - 空間統計手法の適用（Moran's I）

5. **研究の限界（Limitations）**:
   - 横断研究（因果推論不可）
   - 生態学的研究デザインの限界
   - 曝露評価の妥当性（測定局偏在）
   - 多重共線性の影響
   - PM2.5単独効果に対する検出力の限界

6. **今後の研究への示唆**:
   - 個人レベルコホート研究の必要性
   - より精緻な曝露評価（個人曝露測定、衛星データ）
   - より長期の曝露期間（10年以上）
   - 交絡因子の包括的測定

---

### 推奨作業（Should Do）

#### 2. **Phase 7b: 追加可視化** 🟢

**必要な図表**:

1. **Figure 1: 地理的分布（Choropleth map）**
   - (A) PM2.5濃度
   - (B) HbA1c平均値
   - (C) 糖尿病処方薬/10万人

2. **Figure 2: 散布図 + 回帰直線**
   - (A) PM2.5 vs HbA1c（95%CI付き）
   - (B) PM2.5 vs 処方薬（95%CI付き）

3. **Figure 3: 残差診断プロット**
   - (A) Residuals vs Fitted
   - (B) Q-Q plot
   - (C) Scale-Location plot
   - (D) Residuals vs Leverage

4. **Figure 4: 測定局分布マップ**
   - 都道府県別測定局数（都市部偏在を可視化）

5. **Table 1: 都道府県別記述統計**
   - PM2.5、HbA1c、処方薬の上位10・下位10都道府県

---

#### 3. **Phase 7c: 追加データ統合** 🟢

**補強可能なデータ**:

1. **都市化率・人口密度**（e-Stat）
2. **医療機関密度**（医療施設調査）
3. **健診受診率**（特定健診実施率）
4. **気象データ**（気温、湿度）- PM2.5との交互作用
5. **複数年NDBデータ**（2018-2022年）- 時系列分析

---

## 📁 ファイル構造

```
projects/NDB_XXX_PM25_diabetes/
├── analysis/
│   ├── 01_extract_pm25.py              ✅ Phase 1
│   ├── 02_extract_hba1c.py             ✅ Phase 2
│   ├── 03_extract_diabetes_prescription.py  ✅ Phase 3
│   ├── 04_integrate_data.py            ✅ Phase 4
│   ├── 05_descriptive_statistics.py    ✅ Phase 5
│   ├── 06_regression_analysis.py       ✅ Phase 6
│   ├── 06b_regression_reduced_model.py ✅ Phase 6b
│   ├── 06c_sensitivity_analysis.py   ✅ Phase 6c
│   ├── 06d_power_analysis.py         ✅ Phase 6d
│   └── (07_final_report.py)            ⏳ 未実施
│
├── data/
│   ├── interim/
│   │   ├── pm25_by_prefecture.csv              ✅ Phase 1出力
│   │   ├── hba1c_by_prefecture.csv             ✅ Phase 2出力
│   │   ├── diabetes_prescription_by_prefecture.csv  ✅ Phase 3出力
│   │   └── analysis_dataset.csv                ✅ Phase 4出力（最終統合データ）
│   │
│   └── raw/
│       ├── soramame_2022_2023.csv              ✅ SORAMAME生データ
│       └── (NDB生データは02_Data/raw/NDB_OpenData/No.10/ に格納)
│
├── results/
│   ├── reports/
│   │   ├── descriptive_statistics.csv          ✅ Phase 5
│   │   ├── correlation_matrix.csv              ✅ Phase 5
│   │   ├── vif_results.csv                     ✅ Phase 6
│   │   ├── regression_results_ols_model1.txt   ✅ Phase 6
│   │   ├── morans_i_model1.txt                 ✅ Phase 6
│   │   ├── regression_results_ols_model2.txt   ✅ Phase 6
│   │   ├── morans_i_model2.txt                 ✅ Phase 6
│   │   ├── vif_results_reduced.csv          ✅ Phase 6b
│   │   ├── regression_results_ols_model1_reduced.txt ✅ Phase 6b
│   │   ├── morans_i_model1_reduced.txt      ✅ Phase 6b
│   │   ├── regression_results_ols_model2_reduced.txt ✅ Phase 6b
│   │   ├── morans_i_model2_reduced.txt      ✅ Phase 6b
│   │   ├── sensitivity_analysis_results.txt ✅ Phase 6c
│   │   └── power_analysis_results.txt     ✅ Phase 6d
│   │
│   └── figures/
│       ├── histograms.png                      ✅ Phase 5 (300 dpi)
│       ├── correlation_heatmap.png             ✅ Phase 5 (300 dpi)
│       ├── scatterplot_matrix.png              ✅ Phase 5 (300 dpi)
│       └── (choropleth_map.png)                ⏳ Phase 7予定
│
├── HANDOVER.md                         ✅ 本ファイル
└── README.md                            ⏳ 未作成
```

---

## 🔄 再現手順

### 環境構築

```bash
# 仮想環境作成
python -m venv .venv

# 仮想環境有効化（Windows）
.venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### 必要なライブラリ

```
pandas>=2.1.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.11.0
statsmodels>=0.14.0
libpysal>=4.9.0
esda>=2.5.0
spreg>=1.4.0
geopandas>=0.14.0  # Phase 7で使用
```

---

### 解析実行手順

```bash
# 作業ディレクトリに移動
cd projects/NDB_XXX_PM25_diabetes

# Phase 1: PM2.5データ抽出
python analysis/01_extract_pm25.py

# Phase 2: HbA1cデータ抽出
python analysis/02_extract_hba1c.py

# Phase 3: 糖尿病処方薬データ抽出
python analysis/03_extract_diabetes_prescription.py

# Phase 4: データ統合
python analysis/04_integrate_data.py

# Phase 5: 記述統計・EDA
python analysis/05_descriptive_statistics.py

# Phase 6: 回帰分析
python analysis/06_regression_analysis.py

# Phase 6b: 縮約モデル回帰分析
python analysis/06b_regression_reduced_model.py

# Phase 6c: 感度分析
python analysis/06c_sensitivity_analysis.py

# Phase 6d: 検出力計算
python analysis/06d_power_analysis.py

# Phase 7: 最終レポート（未実施）
# python analysis/07_final_report.py
```

**実行時間**: 各フェーズ1-5分程度、合計約30分

---

## 📌 次ステップの推奨

### 優先度A（必須）

1. **Phase 7a: Discussion徹底強化**
   - 4000-5000語の詳細考察
   - 所要時間: 1-2週間

---

### 優先度B（推奨）

2. **Phase 7b: 追加可視化**
   - Choropleth map作成
   - 残差診断プロット
   - 所要時間: 1日

3. **Phase 7c: 追加データ統合**
   - 都市化率、医療機関密度等
   - 所要時間: 2-3日

---

### 優先度C（オプション）

4. **Ridge回帰・PCA解析**
   - 多重共線性への代替アプローチ
   - 所要時間: 1日

5. **時系列データ統合**
   - 複数年NDBデータの解析
   - 所要時間: 1週間

---

## 💡 重要な注意事項

### セキュリティ・コンプライアンス

1. **NDB生データの取り扱い**
   - `02_Data/raw/NDB_OpenData/` は絶対に変更禁止
   - AIへの実データ送信禁止
   - スクリーンショットにデータを含めない

2. **共変量データの出典明記**
   - 現在、COVARIATES_DATAが埋め込みコード
   - 公的統計（e-Stat等）からの再取得推奨
   - 出典をMethodsセクションに明記

3. **倫理審査**
   - NDB Open Dataは公開データ（倫理審査不要）
   - ただし、機関によっては事前承認が必要

---

### 統計解析上の注意

1. **多重共線性の問題**
   - 縮約モデルでもVIFが残存
   - Discussion/Limitationsで明記
   - Ridge/PCAは補助解析として検討

2. **PM2.5単独効果の検出力**
   - モデル全体の検出力は十分
   - ただし部分効果は小さく検出が難しい
   - 「関連なし」の解釈は慎重に

3. **生態学的誤謬**
   - 都道府県レベルの関連 ≠ 個人レベルの関連
   - 因果推論は不可（横断研究）
   - Discussionで徹底的に議論

---

### 論文執筆上の注意

1. **ネガティブ結果の報告**
   - 主要仮説が棄却されても学術的価値あり
   - "Absence of evidence is not evidence of absence"
   - Discussionで十分な考察を

2. **STROBE声明の遵守**
   - 観察研究の報告ガイドライン
   - チェックリスト: https://www.strobe-statement.org/

3. **データ・コード公開**
   - PLOS ONE等はデータ公開義務
   - GitHub/OSFでコード公開推奨
   - NDB生データは非公開（利用規約上）

---

## 📞 引き継ぎ時の連絡事項

### 既知の問題

1. **UnicodeEncodeError（解決済み）**
   - Windows consoleのcp932エンコーディング問題
   - 特殊文字（⚠️、→、²、≥）をASCII文字に置換済み

2. **沖縄県の孤立（Warning）**
   - 空間重み行列で沖縄県が孤立ノード
   - Moran's I計算時にWarning表示（正常動作）

3. **型不一致エラー（解決済み）**
   - prefecture_code（int64 vs str）の型不一致
   - Phase 4でdefensive copy + zero-paddingで解決

---

### 参考資料

1. **NDB Open Data利用ガイド**
   - https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

2. **環境省SORAMAME**
   - https://soramame.env.go.jp/

3. **空間統計（PySAL）ドキュメント**
   - https://pysal.org/

4. **STROBE声明（観察研究報告ガイドライン）**
   - https://www.strobe-statement.org/

---

## 📝 更新履歴

| 日付 | 更新者 | 内容 |
|------|--------|------|
| 2026-03-12 | Antigravity | Phase 6b-6d反映・HANDOVER整合性更新 |
| 2026-03-12 | Claude Sonnet 4.5 | 初版作成（Phase 1-6完了時点） |

---

**次の作業者へ**: Phase 6dまでの解析工程（感度分析、統計的検出力計算を含む）がすべて完了しました。多重共線性の問題は縮約モデルである程度緩和されましたが、最終的なネガティブ結果の解釈に不可欠な十分なDiscussionの記述（Phase 7a）へ移行してください。その後、視覚的なレポート作成（Phase 7b）に進むことで論文化が可能です。

**ご質問・不明点**: このHANDOVER.mdに追記してください。

---

**Status**: 🟡 **Phase 7作業待ち**（解析完了済 → Discussion徹底強化 → 追加可視化作成 → 論文完成へ）








