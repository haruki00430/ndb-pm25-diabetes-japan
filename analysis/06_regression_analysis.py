"""
Phase 6: 回帰分析（OLS + 空間回帰）

PM2.5とHbA1c/糖尿病処方薬の関連を検証：
1. OLS回帰（共変量調整）
2. VIFチェック（多重共線性）
3. Moran's I検定（空間的自己相関）
4. 空間回帰モデル（SLM/SEM）
"""

import sys
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm

# PySAL系のインポート
try:
    from libpysal.weights import W
    from esda.moran import Moran
    from spreg import OLS as Spreg_OLS, ML_Lag, ML_Error
    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False
    warnings.warn("PySAL not available. Spatial analysis will be skipped.")

# ndb_libraryのインポート
try:
    from ndb_library.viz import set_japanese_font
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parents[3] / 'src'))
    from ndb_library.viz import set_japanese_font

# 日本語フォント設定（必須）
set_japanese_font()

# ============================
# 設定
# ============================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / 'data' / 'interim'
RESULTS_DIR = PROJECT_ROOT / 'results'
REPORTS_DIR = RESULTS_DIR / 'reports'
FIGURES_DIR = RESULTS_DIR / 'figures'

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# ============================
# 都道府県隣接行列の定義
# ============================
def create_prefecture_adjacency_matrix():
    """
    都道府県の隣接行列を手動で定義（Queen contiguity）

    Returns:
        neighbors (dict): {prefecture_code: [adjacent_prefecture_codes]}
    """
    # 都道府県の隣接関係（JIS X 0401コード）
    neighbors = {
        '01': ['02'],  # 北海道 - 青森（青函トンネル）
        '02': ['01', '03', '05'],  # 青森 - 北海道、岩手、秋田
        '03': ['02', '04', '05'],  # 岩手 - 青森、宮城、秋田
        '04': ['03', '05', '06', '07'],  # 宮城 - 岩手、秋田、山形、福島
        '05': ['02', '03', '04', '06'],  # 秋田 - 青森、岩手、宮城、山形
        '06': ['04', '05', '07', '15'],  # 山形 - 宮城、秋田、福島、新潟
        '07': ['04', '06', '08', '09', '15'],  # 福島 - 宮城、山形、茨城、栃木、新潟
        '08': ['07', '09', '11', '12'],  # 茨城 - 福島、栃木、埼玉、千葉
        '09': ['07', '08', '10', '11'],  # 栃木 - 福島、茨城、群馬、埼玉
        '10': ['09', '11', '15', '20'],  # 群馬 - 栃木、埼玉、新潟、長野
        '11': ['08', '09', '10', '12', '13', '19'],  # 埼玉 - 茨城、栃木、群馬、千葉、東京、山梨
        '12': ['08', '11', '13'],  # 千葉 - 茨城、埼玉、東京
        '13': ['11', '12', '14', '19'],  # 東京 - 埼玉、千葉、神奈川、山梨
        '14': ['13', '19', '22'],  # 神奈川 - 東京、山梨、静岡
        '15': ['06', '07', '10', '16', '17', '20'],  # 新潟 - 山形、福島、群馬、富山、石川、長野
        '16': ['15', '17', '20', '21'],  # 富山 - 新潟、石川、長野、岐阜
        '17': ['15', '16', '18', '21'],  # 石川 - 新潟、富山、福井、岐阜
        '18': ['17', '21', '25', '26'],  # 福井 - 石川、岐阜、滋賀、京都
        '19': ['11', '13', '14', '20', '22'],  # 山梨 - 埼玉、東京、神奈川、長野、静岡
        '20': ['10', '15', '16', '19', '21', '22', '23'],  # 長野 - 群馬、新潟、富山、山梨、岐阜、静岡、愛知
        '21': ['16', '17', '18', '20', '23', '24', '25'],  # 岐阜 - 富山、石川、福井、長野、愛知、三重、滋賀
        '22': ['14', '19', '20', '23'],  # 静岡 - 神奈川、山梨、長野、愛知
        '23': ['20', '21', '22', '24'],  # 愛知 - 長野、岐阜、静岡、三重
        '24': ['21', '23', '25', '26', '29', '30'],  # 三重 - 岐阜、愛知、滋賀、京都、奈良、和歌山
        '25': ['18', '21', '24', '26'],  # 滋賀 - 福井、岐阜、三重、京都
        '26': ['18', '24', '25', '27', '28', '29'],  # 京都 - 福井、三重、滋賀、大阪、兵庫、奈良
        '27': ['26', '28', '30'],  # 大阪 - 京都、兵庫、和歌山
        '28': ['26', '27', '31', '33', '34', '36'],  # 兵庫 - 京都、大阪、鳥取、岡山、香川、徳島（？）
        '29': ['24', '26', '30'],  # 奈良 - 三重、京都、和歌山
        '30': ['24', '27', '29'],  # 和歌山 - 三重、大阪、奈良
        '31': ['28', '32', '33', '34'],  # 鳥取 - 兵庫、島根、岡山、広島（？）
        '32': ['31', '34'],  # 島根 - 鳥取、広島
        '33': ['28', '31', '34'],  # 岡山 - 兵庫、鳥取、広島
        '34': ['28', '31', '32', '33', '35'],  # 広島 - 兵庫（？）、鳥取、島根、岡山、山口
        '35': ['34', '40'],  # 山口 - 広島、福岡（関門海峡）
        '36': ['37', '38', '39'],  # 徳島 - 香川、愛媛、高知
        '37': ['36', '38', '39'],  # 香川 - 徳島、愛媛、高知
        '38': ['36', '37', '39'],  # 愛媛 - 徳島、香川、高知
        '39': ['36', '37', '38'],  # 高知 - 徳島、香川、愛媛
        '40': ['35', '41', '42', '44'],  # 福岡 - 山口、佐賀、長崎、大分
        '41': ['40', '42'],  # 佐賀 - 福岡、長崎
        '42': ['40', '41', '43'],  # 長崎 - 福岡、佐賀、熊本
        '43': ['40', '42', '44', '45', '46'],  # 熊本 - 福岡、長崎、大分、宮崎、鹿児島
        '44': ['40', '43', '45'],  # 大分 - 福岡、熊本、宮崎
        '45': ['43', '44', '46'],  # 宮崎 - 熊本、大分、鹿児島
        '46': ['43', '45'],  # 鹿児島 - 熊本、宮崎
        '47': [],  # 沖縄 - 隣接なし（孤立）
    }

    return neighbors


def create_spatial_weights(df: pd.DataFrame, neighbors: dict):
    """
    隣接行列からlibpysal.weights.Wオブジェクトを作成

    Args:
        df: DataFrame with 'prefecture_code' column
        neighbors: adjacency dictionary

    Returns:
        W: libpysal weights object
    """
    if not PYSAL_AVAILABLE:
        return None

    # prefecture_codeの順序でインデックスを作成
    pref_codes = df['prefecture_code'].astype(str).str.zfill(2).tolist()

    # 隣接リストをインデックスベースに変換
    neighbors_idx = {}
    pref_to_idx = {code: idx for idx, code in enumerate(pref_codes)}

    for pref_code in pref_codes:
        adj_codes = neighbors.get(pref_code, [])
        neighbors_idx[pref_to_idx[pref_code]] = [pref_to_idx[c] for c in adj_codes if c in pref_to_idx]

    # Wオブジェクト作成
    w = W(neighbors_idx)
    w.transform = 'R'  # 行標準化

    return w


# ============================
# データ読み込み
# ============================
def load_data():
    """analysis_dataset.csvを読み込む"""
    file_path = DATA_DIR / 'analysis_dataset.csv'
    df = pd.read_csv(file_path, dtype={'prefecture_code': str}, encoding='utf-8')

    # prefecture_codeをゼロ埋め2桁に統一
    df['prefecture_code'] = df['prefecture_code'].str.zfill(2)

    print(f"データ読み込み完了: {len(df)} 都道府県")
    print(f"カラム: {df.columns.tolist()}")

    return df


# ============================
# OLS回帰分析
# ============================
def run_ols_regression(df: pd.DataFrame, y_var: str, x_vars: list, output_file: Path):
    """
    OLS回帰を実行し、結果を保存

    Args:
        df: データフレーム
        y_var: 従属変数名
        x_vars: 独立変数名のリスト
        output_file: 結果出力ファイルパス
    """
    # 欠損値除外
    df_clean = df[[y_var] + x_vars].dropna()
    n = len(df_clean)

    print(f"\n{'='*60}")
    print(f"OLS回帰: {y_var} ~ {' + '.join(x_vars)}")
    print(f"サンプルサイズ: {n} 都道府県")
    print(f"{'='*60}\n")

    # 独立変数行列（定数項を追加）
    X = df_clean[x_vars].values
    X = sm.add_constant(X)

    # 従属変数
    y = df_clean[y_var].values

    # OLS推定
    model = sm.OLS(y, X)
    results = model.fit()

    # 結果の保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"OLS回帰分析結果\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"従属変数: {y_var}\n")
        f.write(f"独立変数: {', '.join(x_vars)}\n")
        f.write(f"サンプルサイズ: {n}\n\n")
        f.write(results.summary().as_text())
        f.write(f"\n\n{'='*60}\n")
        f.write(f"診断統計量\n")
        f.write(f"{'='*60}\n")
        f.write(f"R-squared: {results.rsquared:.4f}\n")
        f.write(f"Adjusted R-squared: {results.rsquared_adj:.4f}\n")
        f.write(f"F-statistic: {results.fvalue:.4f} (p={results.f_pvalue:.4e})\n")
        f.write(f"AIC: {results.aic:.2f}\n")
        f.write(f"BIC: {results.bic:.2f}\n")
        f.write(f"Durbin-Watson: {sm.stats.stattools.durbin_watson(results.resid):.4f}\n")

        # Shapiro-Wilk検定（残差の正規性）
        shapiro_stat, shapiro_p = stats.shapiro(results.resid)
        f.write(f"\n正規性検定（Shapiro-Wilk）:\n")
        f.write(f"  W = {shapiro_stat:.4f}, p = {shapiro_p:.4f}\n")
        if shapiro_p > 0.05:
            f.write(f"  -> 残差は正規分布に従う（p > 0.05）\n")
        else:
            f.write(f"  -> 残差は正規分布に従わない（p < 0.05）\n")

    print(f"結果を保存: {output_file.name}")
    print(f"R^2 = {results.rsquared:.4f}, Adj. R^2 = {results.rsquared_adj:.4f}")

    return results, df_clean


# ============================
# VIF計算
# ============================
def calculate_vif(df: pd.DataFrame, x_vars: list, output_file: Path):
    """
    多重共線性チェック（VIF）

    Args:
        df: データフレーム
        x_vars: 独立変数名のリスト
        output_file: 結果出力ファイルパス
    """
    print(f"\n{'='*60}")
    print(f"VIF（多重共線性チェック）")
    print(f"{'='*60}\n")

    # 欠損値除外
    df_clean = df[x_vars].dropna()

    # VIF計算
    vif_data = pd.DataFrame()
    vif_data['Variable'] = x_vars
    vif_data['VIF'] = [variance_inflation_factor(df_clean.values, i) for i in range(len(x_vars))]

    # 判定
    vif_data['判定'] = vif_data['VIF'].apply(lambda x: 'OK' if x < 10 else '要注意（VIF>=10）')

    # UTF-8でファイルに書き込んでから読み込み（コンソールエンコーディングエラー回避）
    vif_str = vif_data.to_string(index=False)
    print(vif_str.encode('cp932', errors='replace').decode('cp932'))

    # 保存
    vif_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nVIF結果を保存: {output_file.name}")

    # 警告
    high_vif = vif_data[vif_data['VIF'] >= 10]
    if len(high_vif) > 0:
        print(f"\n[WARNING] 以下の変数でVIF>=10（多重共線性の可能性）")
        for _, row in high_vif.iterrows():
            print(f"  - {row['Variable']}: VIF = {row['VIF']:.2f}")

    return vif_data


# ============================
# Moran's I検定
# ============================
def test_spatial_autocorrelation(residuals: np.ndarray, w, output_file: Path):
    """
    Moran's I検定（残差の空間的自己相関）

    Args:
        residuals: OLS回帰の残差
        w: 空間重み行列
        output_file: 結果出力ファイルパス
    """
    if not PYSAL_AVAILABLE:
        print("[WARNING] PySALが利用できないため、空間的自己相関検定をスキップします。")
        return None

    print(f"\n{'='*60}")
    print(f"Moran's I検定（残差の空間的自己相関）")
    print(f"{'='*60}\n")

    # Moran's I計算
    moran = Moran(residuals, w, permutations=9999)

    print(f"Moran's I: {moran.I:.4f}")
    print(f"期待値: {moran.EI:.4f}")
    print(f"p値: {moran.p_sim:.4f}")

    # 判定
    if moran.p_sim < 0.05:
        print(f"-> 有意な空間的自己相関あり（p < 0.05）")
        print(f"  空間回帰モデル（SLM/SEM）の検討が必要")
        spatial_autocorr = True
    else:
        print(f"-> 有意な空間的自己相関なし（p >= 0.05）")
        print(f"  OLS回帰で十分")
        spatial_autocorr = False

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Moran's I 検定結果\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Moran's I: {moran.I:.4f}\n")
        f.write(f"期待値 (E[I]): {moran.EI:.4f}\n")
        f.write(f"分散 (Var[I]): {moran.VI_norm:.6f}\n")
        f.write(f"Z値: {moran.z_norm:.4f}\n")
        f.write(f"p値（モンテカルロ, n=9999）: {moran.p_sim:.4f}\n\n")

        if spatial_autocorr:
            f.write(f"判定: 有意な空間的自己相関あり（p < 0.05）\n")
            f.write(f"推奨: 空間回帰モデル（SLM/SEM）の検討が必要\n")
        else:
            f.write(f"判定: 有意な空間的自己相関なし（p >= 0.05）\n")
            f.write(f"推奨: OLS回帰で十分\n")

    print(f"\nMoran's I結果を保存: {output_file.name}")

    return moran, spatial_autocorr


# ============================
# 空間回帰モデル
# ============================
def run_spatial_regression(df: pd.DataFrame, y_var: str, x_vars: list, w,
                          output_file_slm: Path, output_file_sem: Path):
    """
    空間回帰モデル（SLM/SEM）を実行

    Args:
        df: データフレーム
        y_var: 従属変数名
        x_vars: 独立変数名のリスト
        w: 空間重み行列
        output_file_slm: SLM結果出力ファイルパス
        output_file_sem: SEM結果出力ファイルパス
    """
    if not PYSAL_AVAILABLE:
        print("[WARNING] PySALが利用できないため、空間回帰モデルをスキップします。")
        return None, None

    # 欠損値除外
    df_clean = df[[y_var] + x_vars].dropna()

    X = df_clean[x_vars].values
    y = df_clean[y_var].values.reshape(-1, 1)

    print(f"\n{'='*60}")
    print(f"空間回帰モデル")
    print(f"{'='*60}\n")

    # ====================
    # Spatial Lag Model (SLM)
    # ====================
    print("Spatial Lag Model (SLM) を推定中...")
    slm = ML_Lag(y, X, w=w, name_y=y_var, name_x=x_vars)

    print(f"  rho (空間ラグ係数): {slm.rho:.4f}")
    print(f"  AIC: {slm.aic:.2f}")
    print(f"  Pseudo R^2: {slm.pr2:.4f}")

    # 結果保存
    with open(output_file_slm, 'w', encoding='utf-8') as f:
        f.write(f"Spatial Lag Model (SLM) 結果\n")
        f.write(f"{'='*60}\n\n")
        f.write(slm.summary)

    print(f"SLM結果を保存: {output_file_slm.name}")

    # ====================
    # Spatial Error Model (SEM)
    # ====================
    print("\nSpatial Error Model (SEM) を推定中...")
    sem = ML_Error(y, X, w=w, name_y=y_var, name_x=x_vars)

    # lambdaの取得
    lambda_coef = sem.betas.flatten()[-1]

    print(f"  lambda (空間誤差係数): {lambda_coef:.4f}")
    print(f"  AIC: {sem.aic:.2f}")
    print(f"  Pseudo R^2: {sem.pr2:.4f}")

    # 結果保存
    with open(output_file_sem, 'w', encoding='utf-8') as f:
        f.write(f"Spatial Error Model (SEM) 結果\n")
        f.write(f"{'='*60}\n\n")
        f.write(sem.summary)

    print(f"SEM結果を保存: {output_file_sem.name}")

    return slm, sem


# ============================
# メイン処理
# ============================
def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("Phase 6: 回帰分析（OLS + 空間回帰）")
    print("="*60 + "\n")

    # データ読み込み
    df = load_data()

    # 独立変数（共変量）
    covariates = ['Aging_Rate', 'Obesity_Rate', 'Smoking_Rate', 'Exercise_Rate', 'GDP_Per_Capita']

    # 主要な独立変数を追加
    x_vars = ['PM25_Mean'] + covariates

    # VIF計算
    vif_output = REPORTS_DIR / 'vif_results.csv'
    calculate_vif(df, x_vars, vif_output)

    # 都道府県隣接行列作成
    neighbors = create_prefecture_adjacency_matrix()
    w = create_spatial_weights(df, neighbors)

    # ============================
    # Model 1: PM25_Mean -> HbA1c_Mean
    # ============================
    print("\n" + "="*60)
    print("Model 1: PM25_Mean -> HbA1c_Mean")
    print("="*60)

    ols1_output = REPORTS_DIR / 'regression_results_ols_model1.txt'
    results1, df_clean1 = run_ols_regression(df, 'HbA1c_Mean', x_vars, ols1_output)

    # Moran's I検定
    if w is not None:
        moran1_output = REPORTS_DIR / 'morans_i_model1.txt'
        moran1, spatial_autocorr1 = test_spatial_autocorrelation(results1.resid, w, moran1_output)

        # 空間的自己相関が有意な場合、空間回帰モデルを実行
        if spatial_autocorr1:
            slm1_output = REPORTS_DIR / 'regression_results_slm_model1.txt'
            sem1_output = REPORTS_DIR / 'regression_results_sem_model1.txt'
            run_spatial_regression(df_clean1, 'HbA1c_Mean', x_vars, w, slm1_output, sem1_output)

    # ============================
    # Model 2: PM25_Mean -> Diabetes_Prescription_Per100k
    # ============================
    print("\n" + "="*60)
    print("Model 2: PM25_Mean -> Diabetes_Prescription_Per100k")
    print("="*60)

    ols2_output = REPORTS_DIR / 'regression_results_ols_model2.txt'
    results2, df_clean2 = run_ols_regression(df, 'Diabetes_Prescription_Per100k', x_vars, ols2_output)

    # Moran's I検定
    if w is not None:
        moran2_output = REPORTS_DIR / 'morans_i_model2.txt'
        moran2, spatial_autocorr2 = test_spatial_autocorrelation(results2.resid, w, moran2_output)

        # 空間的自己相関が有意な場合、空間回帰モデルを実行
        if spatial_autocorr2:
            slm2_output = REPORTS_DIR / 'regression_results_slm_model2.txt'
            sem2_output = REPORTS_DIR / 'regression_results_sem_model2.txt'
            run_spatial_regression(df_clean2, 'Diabetes_Prescription_Per100k', x_vars, w, slm2_output, sem2_output)

    print("\n" + "="*60)
    print("Phase 6 完了")
    print("="*60)
    print(f"\n出力ファイル:")
    print(f"  - VIF: {vif_output.name}")
    print(f"  - Model 1 OLS: {ols1_output.name}")
    print(f"  - Model 1 Moran's I: {moran1_output.name if w else 'スキップ'}")
    print(f"  - Model 2 OLS: {ols2_output.name}")
    print(f"  - Model 2 Moran's I: {moran2_output.name if w else 'スキップ'}")


if __name__ == '__main__':
    main()

