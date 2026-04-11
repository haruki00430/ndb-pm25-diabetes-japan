# NDB_XXX_PM25_diabetes

**プロジェクト名**: PM2.5曝露と糖尿病関連指標の都道府県別生態学的研究
**開始日**: 2026-03-11
**ステータス**: 解析パイプライン実行済・レポート・Quarto 原稿あり（2026-04-05 リポジトリ照合）

**リポジトリ照合メモ（2026-04-05）**: `analysis/01`〜`07` 系スクリプトおよび `06b–06d` が存在。`data/interim/` に PM2.5・HbA1c・処方・統合 CSV。`results/reports/` に記述統計・回帰・Moran's I・感度分析・検定力等の出力。`04_Manuscripts/` に複数 `.qmd`（試行原稿・`_final` 等）。**メインのレンダリング例**は `04_Manuscripts/README.md` の `Manuscript_PM25_diabetes.qmd` を参照。旧 README の「Phase 0 のみ」は実体と不一致だったため本欄を優先する。

---

## プロジェクト概要

### 研究テーマ
大気汚染物質（PM2.5）の長期曝露が糖尿病発症・血糖コントロールに与える影響を、都道府県レベルの生態学的研究デザインで検証する。

### 主要な仮説
- **仮説1**: PM2.5年平均濃度が高い都道府県ほど、HbA1c平均値が高い
- **仮説2**: PM2.5年平均濃度が高い都道府県ほど、糖尿病用剤の処方量が多い

### 研究デザイン
- **デザイン**: 生態学的研究（Ecological study）
- **地理単位**: 都道府県別（N=47）
- **解析手法**:
  - OLS回帰分析（共変量調整）
  - 空間回帰分析（Spatial Lag Model / Spatial Error Model）
  - 感度分析（HbA1c中央値設定、PM2.5集計方法）

---

## データソース

### 1. 曝露変数: PM2.5年平均濃度
- **データ提供**: 国立環境研究所「大気汚染常時監視データ」
- **対象年度**: 2022-2023年度（2年間平均）
- **単位**: μg/m³
- **集計方法**: 都道府県内の全測定局の年平均値を算術平均

### 2. アウトカム変数

#### 2.1 HbA1c平均値
- **データ提供**: 厚生労働省 第10回NDBオープンデータ（特定健診 検査）
- **対象年度**: 令和4年度（2022年4月～2023年3月）
- **単位**: %（NGSP値）
- **計算方法**: HbA1c階層別人数から加重平均を算出

#### 2.2 糖尿病用剤処方量
- **データ提供**: 厚生労働省 第10回NDBオープンデータ（処方薬）
- **対象年度**: 令和5年度（2023年4月～2024年3月）
- **薬効分類**: 396（糖尿病用剤）
- **単位**: 処方数/10万人

### 3. 調整変数（共変量）
- **高齢化率**: 65歳以上人口割合（%）- 政府統計e-Stat
- **BMI肥満率**: BMI≥25の割合（%）- NDB特定健診
- **喫煙率**: 現在習慣的に喫煙している者の割合（%）- NDB特定健診
- **運動習慣率**: 1回30分以上の運動を週2回以上実施（%）- NDB特定健診
- **1人あたり県内総生産**: 県内GDP/人口（万円）- 内閣府

---

## ディレクトリ構造

```
projects/NDB_XXX_PM25_diabetes/
├── README.md                      # このファイル
├── config/
│   └── config.yaml                # プロジェクト設定ファイル
├── data/
│   └── interim/                   # 中間データ（ETL後）
│       ├── pm25_prefecture.csv            # Phase 1出力
│       ├── hba1c_prefecture.csv           # Phase 2出力
│       ├── diabetes_prescription.csv      # Phase 3出力
│       └── analysis_dataset.csv           # Phase 4出力（統合データ）
├── analysis/                      # 解析スクリプト
│   ├── 01_extract_pm25.py                 # Phase 1
│   ├── 02_extract_hba1c.py                # Phase 2
│   ├── 03_extract_diabetes_prescription.py # Phase 3
│   ├── 04_integrate_data.py               # Phase 4
│   ├── 05_descriptive_statistics.py       # Phase 5
│   ├── 06_regression_analysis.py          # Phase 6
│   └── 07_visualization.py                # Phase 7
├── results/                       # 解析結果
│   ├── figures/                   # 図（PNG, 300dpi）
│   │   ├── pm25_choropleth.png
│   │   ├── hba1c_choropleth.png
│   │   ├── correlation_heatmap.png
│   │   ├── scatterplot_pm25_hba1c.png
│   │   └── spatial_autocorrelation.png
│   └── reports/                   # レポート（CSV, TXT）
│       ├── descriptive_statistics.csv
│       ├── correlation_matrix.csv
│       ├── regression_results_ols.txt
│       ├── regression_results_slm.txt
│       └── regression_results_sem.txt
└── docs/                          # ドキュメント
    ├── implementation_plan.md     # 実装計画（7フェーズ）
    ├── data_schema.md             # データスキーマ
    └── sensitivity_analysis.md    # 感度分析の記録
```

---

## 実装フェーズ

### ✅ Phase 0: プロジェクト構造作成
- **完了日**: 2026-03-11
- **成果物**:
  - ディレクトリ構造作成
  - config.yaml作成
  - README.md作成

### ✅ Phase 1: PM2.5データ抽出（スクリプト・中間出力あり）
- **スクリプト**: `analysis/01_extract_pm25.py`
- **入力**: `02_Data/raw/Air_Pollution/TD20221200.zip`, `TD20231200.zip`
- **出力**: `data/interim/pm25_prefecture.csv`
- **処理内容**:
  1. ZIPファイル解凍
  2. Shift-JIS → UTF-8変換
  3. 都道府県別に測定局データを集計
  4. 2022-2023年の2年間平均を計算

### ✅ Phase 2: HbA1cデータ抽出（中間 CSV あり）
- **スクリプト**: `analysis/02_extract_hba1c.py`
- **入力**: NDB特定健診検査ファイル（HbA1c）
- **出力**: `data/interim/hba1c_prefecture.csv`
- **処理内容**:
  1. MultiIndexヘッダーの読み込み
  2. HbA1c階層別人数の抽出
  3. 加重平均の計算（中央値法）

### ✅ Phase 3: 糖尿病用剤データ抽出（中間 CSV あり）
- **スクリプト**: `analysis/03_extract_diabetes_prescription.py`
- **入力**: NDB処方薬ファイル（内服・注射）
- **出力**: `data/interim/diabetes_prescription.csv`
- **処理内容**:
  1. 薬効分類396のフィルタリング
  2. 4ファイル（外来院外・院内、入院、注射）の統合
  3. 人口10万人あたりに標準化

### ✅ Phase 4: データ統合（`analysis_dataset.csv` あり）
- **スクリプト**: `analysis/04_integrate_data.py`
- **入力**: Phase 1-3の出力 + 外部統計データ
- **出力**: `data/interim/analysis_dataset.csv`
- **処理内容**:
  1. 都道府県コードでマージ
  2. 共変量（高齢化率、BMI肥満率等）の追加
  3. 欠損値の確認

### ✅ Phase 5: 記述統計・探索的データ解析（EDA）（`descriptive_statistics.csv` 等あり）
- **スクリプト**: `analysis/05_descriptive_statistics.py`
- **出力**:
  - `results/reports/descriptive_statistics.csv`
  - `results/figures/correlation_heatmap.png`
- **処理内容**:
  1. 基本統計量の算出
  2. 相関行列の計算
  3. ヒストグラム・choropleth map作成

### ✅ Phase 6: 回帰分析（OLS・削減モデル・Moran's I 等のレポートあり）
- **スクリプト**: `analysis/06_regression_analysis.py`
- **出力**:
  - `results/reports/regression_results_ols.txt`
  - `results/reports/regression_results_slm.txt`
  - `results/reports/regression_results_sem.txt`
- **処理内容**:
  1. OLS回帰（共変量調整）
  2. 多重共線性チェック（VIF）
  3. 空間的自己相関テスト（Moran's I）
  4. 空間回帰モデル（SLM/SEM）

### 🔄 Phase 7: 可視化・最終レポート（`final_summary_report.md` 等あり・図フォルダは環境次第で要確認）
- **スクリプト**: `analysis/07_visualization.py`
- **出力**:
  - `results/figures/scatterplot_pm25_hba1c.png`
  - `results/figures/spatial_autocorrelation.png`
  - `results/reports/final_summary_report.md`
- **処理内容**:
  1. 散布図（PM2.5 vs HbA1c/糖尿病用剤）
  2. 空間分布図
  3. Forest plot（回帰係数の可視化）
  4. 最終サマリーレポート作成

---

## 実行方法

### 環境構築
```bash
# 仮想環境の作成と有効化
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 解析実行（Phase 1-7を順番に実行）
```bash
# 作業ディレクトリに移動
cd projects/NDB_XXX_PM25_diabetes

# Phase 1: PM2.5データ抽出
python analysis/01_extract_pm25.py

# Phase 2: HbA1cデータ抽出
python analysis/02_extract_hba1c.py

# Phase 3: 糖尿病用剤データ抽出
python analysis/03_extract_diabetes_prescription.py

# Phase 4: データ統合
python analysis/04_integrate_data.py

# Phase 5: 記述統計・EDA
python analysis/05_descriptive_statistics.py

# Phase 6: 回帰分析
python analysis/06_regression_analysis.py

# Phase 7: 可視化・最終レポート
python analysis/07_visualization.py
```

---

## 主要な課題と対応策

### 1. HbA1c階層の中央値設定の恣意性
- **課題**: 「8.4以上」「5.6未満」の両端階層の中央値設定が恣意的
- **対応**: 感度分析で3シナリオ（Conservative/Moderate/Liberal）をテスト

### 2. 測定局数の都道府県間格差
- **課題**: 東京都86局 vs 鳥取県8局など、測定局数に大きな格差
- **対応**: 測定局数を共変量として追加、またはRobust回帰を使用

### 3. データ年度のズレ
- **課題**: PM2.5（2022-2023）、HbA1c（2022）、処方薬（2023）の年度が完全一致しない
- **対応**: PM2.5を2年平均として使用、Limitationsセクションで明示

### 4. 空間的自己相関
- **課題**: 隣接都道府県間で類似した値を示す可能性（空間的自己相関）
- **対応**: Moran's Iでテスト後、Spatial Lag Model (SLM) / Spatial Error Model (SEM) を適用

### 5. 生態学的研究の限界（Ecological Fallacy）
- **課題**: 都道府県レベルの関連が個人レベルの因果関係を示すとは限らない
- **対応**: Limitationsで個人レベルの因果推論ではないことを明記

---

## 引用文献

### NDBデータ
厚生労働省. 第10回NDBオープンデータ（令和5年度レセプト情報・令和4年度特定健診情報）. https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

### 大気汚染データ
国立環境研究所. 大気汚染常時監視データ（2022-2023年度）. https://tenbou.nies.go.jp/download/

### 関連文献
- Yang BY et al. (2020). Ambient air pollution and diabetes: A systematic review and meta-analysis. *Environ Res*. 180:108817.
- Rajagopalan S et al. (2018). Air pollution and cardiovascular disease. *J Am Coll Cardiol*. 72(17):2054-2070.

---

## ライセンス

このプロジェクトは研究目的のみで使用されます。NDBオープンデータ利用規約に従い、個人を特定できる情報は一切含まれていません。

---

## 更新履歴

- **2026-04-05**: リポジトリ実体に合わせステータス・Phase 1–7 表記を更新（旧「Phase 0 のみ」は誤記）
- **2026-03-11**: Phase 0完了（プロジェクト構造作成）
