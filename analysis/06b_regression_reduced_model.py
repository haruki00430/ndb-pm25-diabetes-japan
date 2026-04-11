#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 6b: 回帰分析（多重共線性解決・変数選択版）

VIFベースの逐次削除により共変量を再設計:
1. 変数選択（VIFしきい値に達するまで逐次削除）
2. OLS回帰（選択済み共変量）
3. VIFチェック（目標: VIF < 10）
4. Moran's I検定（空間的自己相関）
5. 空間回帰モデル（SLM/SEM、必要時のみ）

変更点:
- VIFベースの変数選択を導入（config.yamlで制御）
- 変数削除の過程をログに記録
- 出力ファイルにサフィックス付与
"""

import sys
from pathlib import Path
import warnings
import yaml

import pandas as pd
import numpy as np
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
    from ndb_library.logger import setup_logger
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parents[3] / 'src'))
    from ndb_library.viz import set_japanese_font
    from ndb_library.logger import setup_logger

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

# ログ設定
_script_dir = Path(__file__).resolve().parent
_log_dir = _script_dir / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / '06b_regression_reduced_model.log'
logger = setup_logger(__name__, log_file=str(_log_file))


# ============================
# 設定読み込み
# ============================
def load_config() -> dict:
    """config.yamlを読み込む"""
    config_path = PROJECT_ROOT / 'config' / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def get_selection_config(config: dict) -> dict:
    """変数選択パラメータを取得"""
    analysis_params = config.get('analysis_parameters', {})
    selection = analysis_params.get('variable_selection', {})

    return {
        'vif_threshold': float(analysis_params.get('vif_threshold', 10.0)),
        'keep_variables': selection.get('keep_variables', ['PM25_Mean']),
        'candidate_covariates': selection.get(
            'candidate_covariates',
            ['Aging_Rate', 'Obesity_Rate', 'Smoking_Rate', 'Exercise_Rate', 'GDP_Per_Capita']
        ),
        'min_covariates': int(selection.get('min_covariates', 2)),
        'max_iterations': int(selection.get('max_iterations', 10)),
        'output_suffix': selection.get('output_suffix', 'vifselect'),
        'permutations': int(analysis_params.get('permutations', 9999)),
        'random_seed': int(config.get('reproducibility', {}).get('random_seed', 42))
    }


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

    pref_codes = df['prefecture_code'].astype(str).str.zfill(2).tolist()

    neighbors_idx = {}
    pref_to_idx = {code: idx for idx, code in enumerate(pref_codes)}

    for pref_code in pref_codes:
        adj_codes = neighbors.get(pref_code, [])
        neighbors_idx[pref_to_idx[pref_code]] = [pref_to_idx[c] for c in adj_codes if c in pref_to_idx]

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

    logger.info(f"データ読み込み完了: {len(df)} 都道府県")
    logger.info(f"カラム: {df.columns.tolist()}")

    return df


# ============================
# VIF計算（共通）
# ============================
def compute_vif_table(df: pd.DataFrame, x_vars: list, vif_threshold: float) -> pd.DataFrame:
    """VIFを計算してDataFrameで返す"""
    df_clean = df[x_vars].dropna()

    vif_data = pd.DataFrame()
    vif_data['Variable'] = x_vars
    vif_data['VIF'] = [variance_inflation_factor(df_clean.values, i) for i in range(len(x_vars))]

    threshold_label = f'要注意（VIF>={vif_threshold}）'
    vif_data['判定'] = vif_data['VIF'].apply(lambda x: 'OK' if x < vif_threshold else threshold_label)

    return vif_data


def select_variables_by_vif(
    df: pd.DataFrame,
    base_vars: list,
    candidate_covariates: list,
    vif_threshold: float,
    min_covariates: int,
    max_iterations: int,
    protected_vars: set
) -> tuple:
    """VIFベースで共変量を逐次削除"""
    current_vars = []
    for v in base_vars + candidate_covariates:
        if v not in current_vars:
            current_vars.append(v)

    # 存在しない変数は除外
    missing_vars = [v for v in current_vars if v not in df.columns]
    if missing_vars:
        logger.warning(f"存在しない変数を除外: {missing_vars}")
        current_vars = [v for v in current_vars if v in df.columns]

    dropped = []

    for i in range(max_iterations):
        vif_table = compute_vif_table(df, current_vars, vif_threshold)
        max_vif = float(vif_table['VIF'].max())
        if max_vif <= vif_threshold:
            logger.info(f"VIFしきい値達成: max_vif={max_vif:.2f}")
            break

        covariates = [v for v in current_vars if v not in protected_vars]
        if len(covariates) <= min_covariates:
            logger.warning(
                "VIFしきい値を満たせないが、共変量数が下限に到達。削減を停止します。"
            )
            break

        drop_candidates = [v for v in covariates if v not in protected_vars]
        if not drop_candidates:
            logger.warning("削除可能な変数がありません。削減を停止します。")
            break

        drop_row = (
            vif_table[vif_table['Variable'].isin(drop_candidates)]
            .sort_values('VIF', ascending=False)
            .iloc[0]
        )
        drop_var = drop_row['Variable']
        current_vars.remove(drop_var)
        dropped.append(drop_var)

        logger.info(
            f"VIF削減: iteration={i + 1}, drop={drop_var}, max_vif={max_vif:.2f}"
        )

    final_vif = compute_vif_table(df, current_vars, vif_threshold)
    return current_vars, final_vif, dropped


# ============================
# OLS回帰分析
# ============================
def run_ols_regression(
    df: pd.DataFrame,
    y_var: str,
    x_vars: list,
    output_file: Path,
    selection_note: str
):
    """
    OLS回帰を実行し、結果を保存

    Args:
        df: データフレーム
        y_var: 従属変数名
        x_vars: 独立変数名のリスト
        output_file: 結果出力ファイルパス
        selection_note: 変数選択の注記
    """
    df_clean = df[[y_var] + x_vars].dropna()
    n = len(df_clean)
    dropped_n = len(df) - n

    logger.info(f"OLS回帰: {y_var} ~ {' + '.join(x_vars)}")
    logger.info(f"サンプルサイズ: {n}（欠損除外: {dropped_n}）")

    X = df_clean[x_vars].values
    X = sm.add_constant(X)
    y = df_clean[y_var].values

    model = sm.OLS(y, X)
    results = model.fit()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("OLS回帰分析結果（VIFベース変数選択版）\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"従属変数: {y_var}\n")
        f.write(f"独立変数: {', '.join(x_vars)}\n")
        f.write(f"サンプルサイズ: {n}\n")
        f.write(f"{selection_note}\n\n")
        f.write(results.summary().as_text())
        f.write(f"\n\n{'='*60}\n")
        f.write("診断統計量\n")
        f.write(f"{'='*60}\n")
        f.write(f"R-squared: {results.rsquared:.4f}\n")
        f.write(f"Adjusted R-squared: {results.rsquared_adj:.4f}\n")
        f.write(f"F-statistic: {results.fvalue:.4f} (p={results.f_pvalue:.4e})\n")
        f.write(f"AIC: {results.aic:.2f}\n")
        f.write(f"BIC: {results.bic:.2f}\n")
        f.write(f"Durbin-Watson: {sm.stats.stattools.durbin_watson(results.resid):.4f}\n")

        shapiro_stat, shapiro_p = stats.shapiro(results.resid)
        f.write("\n正規性検定（Shapiro-Wilk）:\n")
        f.write(f"  W = {shapiro_stat:.4f}, p = {shapiro_p:.4f}\n")
        if shapiro_p > 0.05:
            f.write("  -> 残差は正規分布に従う（p > 0.05）\n")
        else:
            f.write("  -> 残差は正規分布に従わない（p < 0.05）\n")

    logger.info(f"結果を保存: {output_file.name}")
    logger.info(f"R^2 = {results.rsquared:.4f}, Adj. R^2 = {results.rsquared_adj:.4f}")

    return results, df_clean


# ============================
# Moran's I検定
# ============================
def test_spatial_autocorrelation(residuals: np.ndarray, w, output_file: Path, permutations: int):
    """
    Moran's I検定（残差の空間的自己相関）

    Args:
        residuals: OLS回帰の残差
        w: 空間重み行列
        output_file: 結果出力ファイルパス
        permutations: モンテカルロ反復回数
    """
    if not PYSAL_AVAILABLE:
        logger.warning("PySALが利用できないため、空間的自己相関検定をスキップします。")
        return None, False

    moran = Moran(residuals, w, permutations=permutations)

    spatial_autocorr = bool(moran.p_sim < 0.05)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Moran's I 検定結果（VIFベース変数選択版）\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Moran's I: {moran.I:.4f}\n")
        f.write(f"期待値 (E[I]): {moran.EI:.4f}\n")
        f.write(f"分散 (Var[I]): {moran.VI_norm:.6f}\n")
        f.write(f"Z値: {moran.z_norm:.4f}\n")
        f.write(f"p値（モンテカルロ, n={permutations}）: {moran.p_sim:.4f}\n\n")

        if spatial_autocorr:
            f.write("判定: 有意な空間的自己相関あり（p < 0.05）\n")
            f.write("推奨: 空間回帰モデル（SLM/SEM）の検討が必要\n")
        else:
            f.write("判定: 有意な空間的自己相関なし（p >= 0.05）\n")
            f.write("推奨: OLS回帰で十分\n")

    logger.info(f"Moran's I結果を保存: {output_file.name}")

    return moran, spatial_autocorr


# ============================
# 空間回帰モデル
# ============================
def run_spatial_regression(
    df: pd.DataFrame,
    y_var: str,
    x_vars: list,
    w,
    output_file_slm: Path,
    output_file_sem: Path
):
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
        logger.warning("PySALが利用できないため、空間回帰モデルをスキップします。")
        return None, None

    df_clean = df[[y_var] + x_vars].dropna()

    X = df_clean[x_vars].values
    y = df_clean[y_var].values.reshape(-1, 1)

    slm = ML_Lag(y, X, w=w, name_y=y_var, name_x=x_vars)

    with open(output_file_slm, 'w', encoding='utf-8') as f:
        f.write("Spatial Lag Model (SLM) 結果（VIFベース変数選択版）\n")
        f.write(f"{'='*60}\n\n")
        f.write(slm.summary)

    logger.info(f"SLM結果を保存: {output_file_slm.name}")

    sem = ML_Error(y, X, w=w, name_y=y_var, name_x=x_vars)

    with open(output_file_sem, 'w', encoding='utf-8') as f:
        f.write("Spatial Error Model (SEM) 結果（VIFベース変数選択版）\n")
        f.write(f"{'='*60}\n\n")
        f.write(sem.summary)

    logger.info(f"SEM結果を保存: {output_file_sem.name}")

    return slm, sem


# ============================
# メイン処理
# ============================
def main():
    """メイン処理"""
    config = load_config()
    selection_cfg = get_selection_config(config)

    np.random.seed(selection_cfg['random_seed'])

    logger.info('=' * 80)
    logger.info('Phase 6b: 回帰分析（VIFベース変数選択版）')
    logger.info('=' * 80)

    df = load_data()

    base_vars = selection_cfg['keep_variables']
    candidate_covariates = selection_cfg['candidate_covariates']
    vif_threshold = selection_cfg['vif_threshold']

    selected_vars, final_vif, dropped_vars = select_variables_by_vif(
        df=df,
        base_vars=base_vars,
        candidate_covariates=candidate_covariates,
        vif_threshold=vif_threshold,
        min_covariates=selection_cfg['min_covariates'],
        max_iterations=selection_cfg['max_iterations'],
        protected_vars=set(base_vars)
    )

    selection_note = (
        f"[変数選択] method=VIF_greedy, threshold={vif_threshold}, "
        f"dropped={dropped_vars if dropped_vars else 'なし'}"
    )

    logger.info(f"選択結果: {selected_vars}")
    logger.info(f"除外変数: {dropped_vars}")

    suffix = selection_cfg['output_suffix']

    # VIF結果出力
    vif_output = REPORTS_DIR / f'vif_results_{suffix}.csv'
    final_vif.to_csv(vif_output, index=False, encoding='utf-8-sig')
    logger.info(f"VIF結果を保存: {vif_output.name}")

    # 都道府県隣接行列作成
    neighbors = create_prefecture_adjacency_matrix()
    w = create_spatial_weights(df, neighbors)

    # ============================
    # Model 1: PM25_Mean -> HbA1c_Mean
    # ============================
    ols1_output = REPORTS_DIR / f'regression_results_ols_model1_{suffix}.txt'
    results1, df_clean1 = run_ols_regression(
        df,
        'HbA1c_Mean',
        selected_vars,
        ols1_output,
        selection_note
    )

    if w is not None:
        moran1_output = REPORTS_DIR / f'morans_i_model1_{suffix}.txt'
        moran1, spatial_autocorr1 = test_spatial_autocorrelation(
            results1.resid,
            w,
            moran1_output,
            selection_cfg['permutations']
        )

        if spatial_autocorr1:
            slm1_output = REPORTS_DIR / f'regression_results_slm_model1_{suffix}.txt'
            sem1_output = REPORTS_DIR / f'regression_results_sem_model1_{suffix}.txt'
            run_spatial_regression(df_clean1, 'HbA1c_Mean', selected_vars, w, slm1_output, sem1_output)

    # ============================
    # Model 2: PM25_Mean -> Diabetes_Prescription_Per100k
    # ============================
    ols2_output = REPORTS_DIR / f'regression_results_ols_model2_{suffix}.txt'
    results2, df_clean2 = run_ols_regression(
        df,
        'Diabetes_Prescription_Per100k',
        selected_vars,
        ols2_output,
        selection_note
    )

    if w is not None:
        moran2_output = REPORTS_DIR / f'morans_i_model2_{suffix}.txt'
        moran2, spatial_autocorr2 = test_spatial_autocorrelation(
            results2.resid,
            w,
            moran2_output,
            selection_cfg['permutations']
        )

        if spatial_autocorr2:
            slm2_output = REPORTS_DIR / f'regression_results_slm_model2_{suffix}.txt'
            sem2_output = REPORTS_DIR / f'regression_results_sem_model2_{suffix}.txt'
            run_spatial_regression(df_clean2, 'Diabetes_Prescription_Per100k', selected_vars, w, slm2_output, sem2_output)

    logger.info('=' * 80)
    logger.info('Phase 6b 完了')
    logger.info('=' * 80)
    logger.info('出力ファイル:')
    logger.info(f'  - VIF: {vif_output.name}')
    logger.info(f'  - Model 1 OLS: {ols1_output.name}')
    logger.info(f'  - Model 2 OLS: {ols2_output.name}')


if __name__ == '__main__':
    main()







