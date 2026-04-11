#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 6c: 感度分析（Sensitivity Analysis）

以下の3つの感度分析を実施:
1. PM2.5測定局数 >= 10 の都道府県に限定
2. Cook's distance による外れ値除外（4/N ルール）
3. 都市部 vs 農村部 の層別解析（人口密度中央値で2分割）

出力: results/reports/sensitivity_analysis_results.txt
"""

import sys
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor, OLSInfluence
import statsmodels.api as sm

# PySAL系のインポート
try:
    from libpysal.weights import W
    from esda.moran import Moran
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
_log_file = _log_dir / '06c_sensitivity_analysis.log'
logger = setup_logger(__name__, log_file=str(_log_file))

# 回帰モデルの変数設定（Phase 6b縮約モデルと同じ）
Y_VARS = ['HbA1c_Mean', 'Diabetes_Prescription_Per100k']
X_VARS = ['PM25_Mean', 'Aging_Rate', 'Obesity_Rate', 'Exercise_Rate', 'GDP_Per_Capita']

# 人口密度（人/km2）データ: 2020年国勢調査ベース（e-Stat）
# 都道府県コード順（01北海道〜47沖縄）
POPULATION_DENSITY = {
    '01': 68.6,   # 北海道
    '02': 129.9,  # 青森
    '03': 83.9,   # 岩手
    '04': 319.6,  # 宮城
    '05': 85.4,   # 秋田
    '06': 118.0,  # 山形
    '07': 135.1,  # 福島
    '08': 470.6,  # 茨城
    '09': 304.5,  # 栃木
    '10': 310.2,  # 群馬
    '11': 1925.0, # 埼玉
    '12': 1207.6, # 千葉
    '13': 6413.0, # 東京
    '14': 3828.7, # 神奈川
    '15': 180.9,  # 新潟
    '16': 248.6,  # 富山
    '17': 274.9,  # 石川
    '18': 87.6,   # 福井
    '19': 187.3,  # 山梨
    '20': 150.0,  # 長野
    '21': 188.2,  # 岐阜
    '22': 476.1,  # 静岡
    '23': 1447.3, # 愛知
    '24': 311.3,  # 三重
    '25': 351.9,  # 滋賀
    '26': 561.8,  # 京都
    '27': 4631.3, # 大阪
    '28': 660.1,  # 兵庫
    '29': 367.3,  # 奈良
    '30': 200.9,  # 和歌山
    '31': 160.9,  # 鳥取
    '32': 102.6,  # 島根
    '33': 270.7,  # 岡山
    '34': 333.6,  # 広島
    '35': 229.6,  # 山口
    '36': 178.2,  # 徳島
    '37': 515.4,  # 香川
    '38': 243.3,  # 愛媛
    '39': 101.0,  # 高知
    '40': 1026.9, # 福岡
    '41': 340.9,  # 佐賀
    '42': 327.9,  # 長崎
    '43': 241.7,  # 熊本
    '44': 184.9,  # 大分
    '45': 140.9,  # 宮崎
    '46': 178.2,  # 鹿児島
    '47': 641.8,  # 沖縄
}


# ============================
# 都道府県隣接行列の定義（Phase 6b流用）
# ============================
def create_prefecture_adjacency_matrix():
    """都道府県の隣接行列を手動で定義（Queen contiguity）"""
    neighbors = {
        '01': ['02'], '02': ['01', '03', '05'], '03': ['02', '04', '05'],
        '04': ['03', '05', '06', '07'], '05': ['02', '03', '04', '06'],
        '06': ['04', '05', '07', '15'], '07': ['04', '06', '08', '09', '15'],
        '08': ['07', '09', '11', '12'], '09': ['07', '08', '10', '11'],
        '10': ['09', '11', '15', '20'], '11': ['08', '09', '10', '12', '13', '19'],
        '12': ['08', '11', '13'], '13': ['11', '12', '14', '19'],
        '14': ['13', '19', '22'], '15': ['06', '07', '10', '16', '17', '20'],
        '16': ['15', '17', '20', '21'], '17': ['15', '16', '18', '21'],
        '18': ['17', '21', '25', '26'], '19': ['11', '13', '14', '20', '22'],
        '20': ['10', '15', '16', '19', '21', '22', '23'],
        '21': ['16', '17', '18', '20', '23', '24', '25'],
        '22': ['14', '19', '20', '23'], '23': ['20', '21', '22', '24'],
        '24': ['21', '23', '25', '26', '29', '30'],
        '25': ['18', '21', '24', '26'], '26': ['18', '24', '25', '27', '28', '29'],
        '27': ['26', '28', '30'], '28': ['26', '27', '31', '33', '34', '36'],
        '29': ['24', '26', '30'], '30': ['24', '27', '29'],
        '31': ['28', '32', '33', '34'], '32': ['31', '34'],
        '33': ['28', '31', '34'], '34': ['28', '31', '32', '33', '35'],
        '35': ['34', '40'], '36': ['37', '38', '39'], '37': ['36', '38', '39'],
        '38': ['36', '37', '39'], '39': ['36', '37', '38'],
        '40': ['35', '41', '42', '44'], '41': ['40', '42'],
        '42': ['40', '41', '43'], '43': ['40', '42', '44', '45', '46'],
        '44': ['40', '43', '45'], '45': ['43', '44', '46'],
        '46': ['43', '45'], '47': [],  # 沖縄は孤立
    }
    return neighbors


def create_spatial_weights(df: pd.DataFrame, neighbors: dict):
    """隣接行列からlibpysal.weights.Wオブジェクトを作成"""
    if not PYSAL_AVAILABLE:
        return None
    pref_codes = df['prefecture_code'].astype(str).str.zfill(2).tolist()
    pref_to_idx = {code: idx for idx, code in enumerate(pref_codes)}
    neighbors_idx = {}
    for pref_code in pref_codes:
        adj_codes = neighbors.get(pref_code, [])
        neighbors_idx[pref_to_idx[pref_code]] = [
            pref_to_idx[c] for c in adj_codes if c in pref_to_idx
        ]
    w = W(neighbors_idx)
    w.transform = 'R'
    return w


# ============================
# データ読み込み
# ============================
def load_data() -> pd.DataFrame:
    """analysis_dataset.csvを読み込む"""
    file_path = DATA_DIR / 'analysis_dataset.csv'
    df = pd.read_csv(file_path, dtype={'prefecture_code': str}, encoding='utf-8')
    df['prefecture_code'] = df['prefecture_code'].str.zfill(2)

    # 人口密度を追加
    df['Population_Density'] = df['prefecture_code'].map(POPULATION_DENSITY)

    logger.info(f"データ読み込み完了: {len(df)} 都道府県")
    logger.info(f"カラム: {df.columns.tolist()}")
    return df


# ============================
# OLS回帰（共通ユーティリティ）
# ============================
def run_ols(df: pd.DataFrame, y_var: str, x_vars: list) -> tuple:
    """
    OLS回帰を実行し、結果オブジェクトと整形済みDataFrameを返す

    Returns:
        (results, df_clean, coeff_pm25, p_pm25, r2_adj)
    """
    df_clean = df[[y_var] + x_vars].dropna()
    X = sm.add_constant(df_clean[x_vars].values)
    y = df_clean[y_var].values
    results = sm.OLS(y, X).fit()
    # PM25_Meanはx_vars[0]（定数項含めると index=1）
    coeff_pm25 = results.params[1]
    p_pm25 = results.pvalues[1]
    r2_adj = results.rsquared_adj
    return results, df_clean, coeff_pm25, p_pm25, r2_adj


def format_model_result(
    label: str,
    y_var: str,
    n: int,
    coeff_pm25: float,
    p_pm25: float,
    r2_adj: float,
    note: str = ""
) -> str:
    """1モデルの結果を整形した文字列として返す"""
    sig = "(*)" if p_pm25 < 0.05 else "(ns)"
    lines = [
        f"  [{label}] {y_var}",
        f"    N={n}, PM25_Mean β={coeff_pm25:.6f}, p={p_pm25:.4f} {sig}",
        f"    Adj.R2={r2_adj:.4f}",
    ]
    if note:
        lines.append(f"    Note: {note}")
    return "\n".join(lines)


# ============================
# 感度分析 1: 測定局数 >= 10 の都道府県に限定
# ============================
def sensitivity_stations(df: pd.DataFrame) -> list:
    """
    感度分析1: PM2.5測定局数 >= 10 の都道府県に限定して回帰

    Returns:
        lines: 結果テキストのリスト
    """
    threshold = 10
    df_sub = df[df['PM25_N_Stations'] >= threshold].copy()
    n_all = len(df)
    n_sub = len(df_sub)

    lines = [
        "=" * 60,
        "感度分析 1: PM2.5測定局数 >= 10 の都道府県に限定",
        "=" * 60,
        f"全都道府県: {n_all}, 限定後: {n_sub} (除外: {n_all - n_sub}都道府県)",
        f"除外された都道府県: {df[df['PM25_N_Stations'] < threshold]['prefecture_name'].tolist()}",
        "",
    ]

    for y_var in Y_VARS:
        try:
            results, df_clean, coeff, p, r2_adj = run_ols(df_sub, y_var, X_VARS)
            lines.append(format_model_result("SA1", y_var, len(df_clean), coeff, p, r2_adj))
        except Exception as e:
            lines.append(f"  [{y_var}] エラー: {e}")
        lines.append("")

    return lines


# ============================
# 感度分析 2: Cook's distance 外れ値除外
# ============================
def sensitivity_cooks(df: pd.DataFrame) -> list:
    """
    感度分析2: Cook's distance > 4/N の都道府県を外れ値として除外

    Returns:
        lines: 結果テキストのリスト
    """
    lines = [
        "=" * 60,
        "感度分析 2: Cook's distance による外れ値除外（閾値: 4/N）",
        "=" * 60,
    ]

    for y_var in Y_VARS:
        logger.info(f"Cook's distance: {y_var}")
        try:
            df_clean_all = df[[y_var] + X_VARS + ['prefecture_code', 'prefecture_name']].dropna()
            n = len(df_clean_all)

            X_full = sm.add_constant(df_clean_all[X_VARS].values)
            y_full = df_clean_all[y_var].values
            results_full = sm.OLS(y_full, X_full).fit()

            influence = OLSInfluence(results_full)
            cooks_d = influence.cooks_distance[0]
            threshold = 4.0 / n

            outlier_idx = np.where(cooks_d > threshold)[0]
            outlier_prefs = df_clean_all.iloc[outlier_idx]['prefecture_name'].tolist()
            outlier_cooks = cooks_d[outlier_idx]

            lines.append(f"  [{y_var}] N={n}, Cook's閾値=4/{n}={threshold:.4f}")
            if len(outlier_idx) > 0:
                for pref, cd in zip(outlier_prefs, outlier_cooks):
                    lines.append(f"    外れ値: {pref} (Cook's d={cd:.4f})")
                # 外れ値除外して再実行
                mask = cooks_d <= threshold
                df_robust = df_clean_all[mask].copy()
                results_robust, _, coeff, p, r2_adj = run_ols(df_robust, y_var, X_VARS)
                lines.append(
                    format_model_result(
                        "SA2", y_var, len(df_robust), coeff, p, r2_adj,
                        note=f"{len(outlier_idx)}都道府県除外({', '.join(outlier_prefs)})"
                    )
                )
            else:
                lines.append(f"    外れ値なし（Cook's d <= {threshold:.4f}）")
                lines.append(
                    format_model_result("SA2", y_var, n,
                                        results_full.params[1], results_full.pvalues[1],
                                        results_full.rsquared_adj,
                                        note="外れ値なし（フルモデルと同じ）")
                )
        except Exception as e:
            lines.append(f"  [{y_var}] エラー: {e}")
        lines.append("")

    return lines


# ============================
# 感度分析 3: 都市部 vs 農村部 層別解析
# ============================
def sensitivity_urban_rural(df: pd.DataFrame) -> list:
    """
    感度分析3: 人口密度の中央値で都市部・農村部に2分割して層別解析

    Returns:
        lines: 結果テキストのリスト
    """
    median_density = df['Population_Density'].median()

    df_urban = df[df['Population_Density'] > median_density].copy()
    df_rural = df[df['Population_Density'] <= median_density].copy()

    lines = [
        "=" * 60,
        "感度分析 3: 都市部 vs 農村部 層別解析",
        "=" * 60,
        f"人口密度中央値: {median_density:.1f} 人/km2",
        f"都市部 (>中央値): {len(df_urban)}都道府県",
        f"農村部 (<=中央値): {len(df_rural)}都道府県",
        "",
        "--- 都市部 ---",
    ]

    for y_var in Y_VARS:
        try:
            results, df_clean, coeff, p, r2_adj = run_ols(df_urban, y_var, X_VARS)
            lines.append(format_model_result("SA3-Urban", y_var, len(df_clean), coeff, p, r2_adj))
        except Exception as e:
            lines.append(f"  [{y_var}] 都市部エラー: {e}")
        lines.append("")

    lines.append("--- 農村部 ---")
    for y_var in Y_VARS:
        try:
            results, df_clean, coeff, p, r2_adj = run_ols(df_rural, y_var, X_VARS)
            lines.append(format_model_result("SA3-Rural", y_var, len(df_clean), coeff, p, r2_adj))
        except Exception as e:
            lines.append(f"  [{y_var}] 農村部エラー: {e}")
        lines.append("")

    return lines


# ============================
# 結果比較サマリー
# ============================
def create_summary_table(full_results: dict, sa1_results: dict,
                          sa2_results: dict, urban_results: dict,
                          rural_results: dict) -> list:
    """
    各感度分析の結果をまとめた比較テーブルを生成

    Args:
        *_results: {y_var: (n, coeff, p, r2_adj)} のdict
    """
    lines = [
        "=" * 60,
        "感度分析 結果比較サマリー",
        "=" * 60,
        "",
    ]

    header = f"{'分析':25s} {'N':>4s} {'PM25_β':>15s} {'p値':>8s} {'有意':>5s} {'Adj.R2':>7s}"
    separator = "-" * 70

    for y_var in Y_VARS:
        lines.append(f"【{y_var}】")
        lines.append(header)
        lines.append(separator)

        rows = [
            ("メインモデル（全47都道府県）", full_results),
            ("SA1: 測定局 >= 10", sa1_results),
            ("SA2: Cook's外れ値除外", sa2_results),
            ("SA3: 都市部", urban_results),
            ("SA3: 農村部", rural_results),
        ]

        for label, res_dict in rows:
            if y_var in res_dict and res_dict[y_var] is not None:
                n, coeff, p, r2_adj = res_dict[y_var]
                sig = "(*)" if p < 0.05 else "(ns)"
                lines.append(
                    f"{label:25s} {n:>4d} {coeff:>15.6f} {p:>8.4f} {sig:>5s} {r2_adj:>7.4f}"
                )
            else:
                lines.append(f"{label:25s} {'NA':>4s} {'NA':>15s} {'NA':>8s} {'NA':>5s} {'NA':>7s}")

        lines.append("")

    return lines


# ============================
# フルモデル（ベースライン）実行
# ============================
def run_full_model(df: pd.DataFrame) -> dict:
    """
    フルモデル（全47都道府県）を実行してベースラインとして使用

    Returns:
        {y_var: (n, coeff, p, r2_adj)}
    """
    results = {}
    for y_var in Y_VARS:
        try:
            _, df_clean, coeff, p, r2_adj = run_ols(df, y_var, X_VARS)
            results[y_var] = (len(df_clean), coeff, p, r2_adj)
        except Exception as e:
            logger.warning(f"フルモデル失敗 ({y_var}): {e}")
            results[y_var] = None
    return results


def extract_result_dict(lines: list) -> dict:
    """
    感度分析の出力テキストから (n, coeff, p, r2_adj) を抽出する簡易パーサー

    Returns:
        {y_var: (n, coeff, p, r2_adj)}
    Note:
        直接計算した方が信頼性が高いため、この関数は補助的に使用
    """
    # この関数は使わず、各SAで直接計算した値を返す方式に変更
    return {}


# ============================
# メイン処理
# ============================
def main():
    """メイン処理"""
    logger.info('=' * 80)
    logger.info('Phase 6c: 感度分析（Sensitivity Analysis）')
    logger.info('=' * 80)

    df = load_data()

    # 都道府県隣接行列と空間重み行列（Moran's I用）
    neighbors = create_prefecture_adjacency_matrix()
    w = create_spatial_weights(df, neighbors)

    # ============================
    # ベースライン（全47都道府県）
    # ============================
    logger.info("ベースライン（フルモデル）実行中...")
    full_results_dict = {}
    for y_var in Y_VARS:
        try:
            _, df_clean, coeff, p, r2_adj = run_ols(df, y_var, X_VARS)
            full_results_dict[y_var] = (len(df_clean), coeff, p, r2_adj)
        except Exception as e:
            logger.warning(f"フルモデル失敗 ({y_var}): {e}")
            full_results_dict[y_var] = None

    # ============================
    # 感度分析 1
    # ============================
    logger.info("感度分析1: 測定局数 >= 10 実行中...")
    sa1_lines = sensitivity_stations(df)
    sa1_results_dict = {}
    df_sa1 = df[df['PM25_N_Stations'] >= 10].copy()
    for y_var in Y_VARS:
        try:
            _, df_clean, coeff, p, r2_adj = run_ols(df_sa1, y_var, X_VARS)
            sa1_results_dict[y_var] = (len(df_clean), coeff, p, r2_adj)
        except Exception:
            sa1_results_dict[y_var] = None

    # ============================
    # 感度分析 2
    # ============================
    logger.info("感度分析2: Cook's distance 外れ値除外 実行中...")
    sa2_lines = sensitivity_cooks(df)
    sa2_results_dict = {}
    for y_var in Y_VARS:
        try:
            df_clean_all = df[[y_var] + X_VARS].dropna()
            n_all = len(df_clean_all)
            X_full = sm.add_constant(df_clean_all[X_VARS].values)
            y_full = df_clean_all[y_var].values
            results_full = sm.OLS(y_full, X_full).fit()
            influence = OLSInfluence(results_full)
            cooks_d = influence.cooks_distance[0]
            mask = cooks_d <= 4.0 / n_all
            df_robust = df_clean_all[mask].copy()
            _, _, coeff, p, r2_adj = run_ols(df_robust, y_var, X_VARS)
            sa2_results_dict[y_var] = (int(mask.sum()), coeff, p, r2_adj)
        except Exception:
            sa2_results_dict[y_var] = None

    # ============================
    # 感度分析 3
    # ============================
    logger.info("感度分析3: 都市部 vs 農村部 層別解析 実行中...")
    sa3_lines = sensitivity_urban_rural(df)
    median_density = df['Population_Density'].median()
    df_urban = df[df['Population_Density'] > median_density].copy()
    df_rural = df[df['Population_Density'] <= median_density].copy()
    urban_results_dict = {}
    rural_results_dict = {}
    for y_var in Y_VARS:
        try:
            _, df_clean, coeff, p, r2_adj = run_ols(df_urban, y_var, X_VARS)
            urban_results_dict[y_var] = (len(df_clean), coeff, p, r2_adj)
        except Exception:
            urban_results_dict[y_var] = None
        try:
            _, df_clean, coeff, p, r2_adj = run_ols(df_rural, y_var, X_VARS)
            rural_results_dict[y_var] = (len(df_clean), coeff, p, r2_adj)
        except Exception:
            rural_results_dict[y_var] = None

    # ============================
    # 比較サマリーテーブル
    # ============================
    summary_lines = create_summary_table(
        full_results_dict,
        sa1_results_dict,
        sa2_results_dict,
        urban_results_dict,
        rural_results_dict,
    )

    # ============================
    # 全結果を1ファイルに書き出し
    # ============================
    output_file = REPORTS_DIR / 'sensitivity_analysis_results.txt'

    header_lines = [
        "Phase 6c: 感度分析 結果レポート",
        "=" * 60,
        "解析日: 2026-03-12",
        f"従属変数: {', '.join(Y_VARS)}",
        f"独立変数（共通）: {', '.join(X_VARS)}",
        "（Smoking_Rateは多重共線性のため除外済み: Phase 6b参照）",
        "",
    ]

    all_lines = (
        header_lines
        + [""]
        + sa1_lines
        + [""]
        + sa2_lines
        + [""]
        + sa3_lines
        + [""]
        + summary_lines
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_lines))

    logger.info(f"感度分析結果を保存: {output_file.name}")

    # ============================
    # コンソールサマリー表示
    # ============================
    print("\n" + "=" * 60)
    print("Phase 6c 感度分析 完了")
    print("=" * 60)
    print(f"出力ファイル: {output_file}")
    print("\n--- 結果サマリー ---")
    for line in summary_lines:
        print(line)

    logger.info("Phase 6c 完了")


if __name__ == '__main__':
    main()
