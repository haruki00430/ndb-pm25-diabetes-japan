#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 6d: 統計的検出力分析（Statistical Power Analysis）

実施内容:
1. Post-hoc power analysis（観測データに基づく効果量から検出力を推定）
2. 必要サンプルサイズ計算（80%検出力を達成するためのN）
3. 効果量ランドスケープ（Cohen's f^2 vs N の検出力曲線）
4. 結果をテキスト + 図（power_curve.png）に出力

出力:
- results/reports/power_analysis_results.txt
- results/figures/power_curve.png
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats

# ndb_library
try:
    from ndb_library.viz import set_japanese_font
    from ndb_library.logger import setup_logger
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parents[3] / 'src'))
    from ndb_library.viz import set_japanese_font
    from ndb_library.logger import setup_logger

# ============================
# 設定
# ============================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR     = PROJECT_ROOT / 'data' / 'interim'
REPORTS_DIR  = PROJECT_ROOT / 'results' / 'reports'
FIGURES_DIR  = PROJECT_ROOT / 'results' / 'figures'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

_log_dir = Path(__file__).resolve().parent / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
logger = setup_logger(__name__, log_file=str(_log_dir / '06d_power_analysis.log'))

# 解析パラメータ（Phase 6b縮約モデルと一致させる）
N_OBS   = 47          # 都道府県数
K_VARS  = 5           # 独立変数数
ALPHA   = 0.05        # 有意水準
TARGET_POWER = 0.80   # 目標検出力

# Phase 6b縮約モデルの R^2 値
R2_MODEL1 = 0.2876    # Model 1: HbA1c_Mean
R2_MODEL2 = 0.2906    # Model 2: Diabetes_Prescription_Per100k

# 効果量の区分（Cohen 1988）
EFFECT_SIZES = {
    'small':  0.02,
    'medium': 0.15,
    'large':  0.35,
}


# ============================
# OLS 回帰の検出力計算（scipy.stats.ncf ベース）
# ============================
def r2_to_f2(r2: float) -> float:
    """R^2 を Cohen's f^2 に変換"""
    return r2 / (1.0 - r2)


def power_ols(f2: float, n: int, k: int, alpha: float = 0.05) -> float:
    """
    OLS 回帰の統計的検出力を計算（非心 F 分布使用）

    Parameters
    ----------
    f2    : Cohen's f^2
    n     : サンプルサイズ
    k     : 独立変数数（切片除く）
    alpha : 有意水準

    Returns
    -------
    power : 統計的検出力
    """
    df1 = k
    df2 = n - k - 1
    if df2 <= 0:
        return float('nan')
    ncp = f2 * n                               # 非心度パラメータ
    f_crit = stats.f.ppf(1.0 - alpha, df1, df2)
    power = 1.0 - stats.ncf.cdf(f_crit, df1, df2, ncp)
    return float(power)


def required_n_ols(f2: float, k: int, alpha: float = 0.05,
                   target_power: float = 0.80, max_n: int = 2000) -> int:
    """
    指定効果量・検出力を達成する最小サンプルサイズを逐次探索

    Returns
    -------
    n : 最小必要サンプルサイズ（見つからない場合は max_n+1）
    """
    for n in range(k + 2, max_n + 1):
        if power_ols(f2, n, k, alpha) >= target_power:
            return n
    return max_n + 1


def effect_size_label(f2: float) -> str:
    """Cohen's f^2 の区分ラベル"""
    if f2 < EFFECT_SIZES['small']:
        return "negligible"
    elif f2 < EFFECT_SIZES['medium']:
        return "small"
    elif f2 < EFFECT_SIZES['large']:
        return "medium"
    else:
        return "large"


# ============================
# 検出力曲線プロット
# ============================
def plot_power_curves(k: int, alpha: float, output_path: Path):
    """
    N vs Power の曲線を複数の Cohen's f^2 でプロット

    オブザーブドな f^2（Model 1, Model 2）も重ねてプロット
    """
    n_range = np.arange(20, 200, 1)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    fig.suptitle(
        "Statistical Power Curves\nPM2.5 and Diabetes Study (NDB_XXX_PM25_diabetes)",
        fontsize=13, fontweight='bold'
    )

    scenarios = [
        # (label, f2, color, linestyle)
        ("negligible (f²=0.01)", 0.01, '#aaaaaa', '--'),
        ("small (f²=0.02)", EFFECT_SIZES['small'], '#74c0fc', '-'),
        ("medium (f²=0.15)", EFFECT_SIZES['medium'], '#51cf66', '-'),
        ("large (f²=0.35)", EFFECT_SIZES['large'], '#ff6b6b', '-'),
    ]

    model_info = [
        (axes[0], "Model 1: HbA1c_Mean", R2_MODEL1),
        (axes[1], "Model 2: Diabetes Medication (per 100,000)", R2_MODEL2),
    ]

    for ax, title, r2 in model_info:
        f2_obs = r2_to_f2(r2)

        # 標準的効果量の曲線
        for label, f2, color, ls in scenarios:
            powers = [power_ols(f2, n, k, alpha) for n in n_range]
            ax.plot(n_range, powers, color=color, linestyle=ls, linewidth=1.5,
                    label=label, alpha=0.85)

        # 観察された効果量（モデルの R^2 相当）
        obs_powers = [power_ols(f2_obs, n, k, alpha) for n in n_range]
        ax.plot(n_range, obs_powers, color='#e67700', linestyle='-', linewidth=2.5,
                label=f"Observed f²={f2_obs:.3f} (R²={r2:.3f})")

        # 現在の N=47 を縦線でマーク
        power_at_47 = power_ols(f2_obs, N_OBS, k, alpha)
        ax.axvline(x=N_OBS, color='#495057', linestyle=':', linewidth=1.5)
        ax.axhline(y=TARGET_POWER, color='#495057', linestyle=':', linewidth=1.5)
        ax.annotate(
            f"N={N_OBS}\nPower={power_at_47:.0%}",
            xy=(N_OBS, power_at_47),
            xytext=(N_OBS + 8, power_at_47 - 0.08),
            fontsize=9,
            arrowprops=dict(arrowstyle='->', color='#495057', lw=1.2),
            color='#495057'
        )

        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Sample size N (number of prefectures)", fontsize=10)
        ax.set_ylabel("Statistical Power", fontsize=10)
        ax.set_ylim(0, 1.02)
        ax.set_xlim(20, 200)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))
        ax.legend(fontsize=8, loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0.80, color='#868e96', linestyle='--', linewidth=1.0, alpha=0.5)
        ax.text(195, 0.81, "80%", ha='right', fontsize=8, color='#868e96')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"検出力曲線を保存: {output_path.name}")


# ============================
# メイン処理
# ============================
def main():
    logger.info('=' * 80)
    logger.info('Phase 6d: 統計的検出力分析')
    logger.info('=' * 80)

    # ============================
    # 1. Post-hoc power（観測 R^2 ベース）
    # ============================
    results_posthoc = {}
    for label, r2 in [("Model 1 (HbA1c_Mean)", R2_MODEL1),
                       ("Model 2 (Diabetes_Prescription_Per100k)", R2_MODEL2)]:
        f2 = r2_to_f2(r2)
        power = power_ols(f2, N_OBS, K_VARS, ALPHA)
        results_posthoc[label] = dict(r2=r2, f2=f2, power=power)
        logger.info(f"{label}: R2={r2:.4f}, f2={f2:.4f}, power={power:.4f}")

    # ============================
    # 2. 必要サンプルサイズ（各効果量で80%検出力）
    # ============================
    required_ns = {}
    for name, f2 in EFFECT_SIZES.items():
        n_req = required_n_ols(f2, K_VARS, ALPHA, TARGET_POWER)
        required_ns[name] = dict(f2=f2, n_required=n_req)

    # モデルの観察効果量でも必要N
    for label, r2 in [("Model 1 obs", R2_MODEL1), ("Model 2 obs", R2_MODEL2)]:
        f2 = r2_to_f2(r2)
        n_req = required_n_ols(f2, K_VARS, ALPHA, TARGET_POWER)
        required_ns[label] = dict(f2=f2, n_required=n_req)

    # ============================
    # 3. テキストレポート出力
    # ============================
    output_file = REPORTS_DIR / 'power_analysis_results.txt'
    lines = [
        "Phase 6d: 統計的検出力分析 結果レポート",
        "=" * 60,
        f"解析日: 2026-03-12",
        f"サンプルサイズ N = {N_OBS}（47都道府県）",
        f"独立変数数 k = {K_VARS}",
        f"有意水準 alpha = {ALPHA}",
        f"目標検出力 = {TARGET_POWER:.0%}",
        "",
        "=" * 60,
        "1. Post-hoc Power（観測 R^2 ベース）",
        "=" * 60,
    ]

    for label, res in results_posthoc.items():
        lines += [
            f"  【{label}】",
            f"    観測 R^2      = {res['r2']:.4f}",
            f"    Cohen's f^2  = {res['f2']:.4f}  ({effect_size_label(res['f2'])})",
            f"    統計的検出力  = {res['power']:.4f} ({res['power']:.1%})",
            f"    判定: {'検出力 >= 80% (十分)' if res['power'] >= 0.80 else '検出力 < 80% (不十分 → Type II error リスクあり)'}",
            "",
        ]

    lines += [
        "=" * 60,
        "2. 必要サンプルサイズ（80%検出力を達成するための N）",
        "=" * 60,
        f"  ({K_VARS}変数モデル, alpha={ALPHA})",
        "",
        f"  {'効果量区分':20s} {'Cohen f²':>10s} {'必要N':>8s} {'現在の N=47 との差':>20s}",
        "  " + "-" * 62,
    ]

    for name, info in required_ns.items():
        diff = info['n_required'] - N_OBS
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        lines.append(
            f"  {name:20s} {info['f2']:>10.3f} {info['n_required']:>8d} {diff_str:>20s}"
        )

    lines += [
        "",
        "=" * 60,
        "3. 解釈と論文記載ポイント",
        "=" * 60,
        "",
        "  N=47（47都道府県）での統計的検出力の評価:",
        f"  - Model 1 (HbA1c): 検出力 ≈ {results_posthoc['Model 1 (HbA1c_Mean)']['power']:.1%}",
        f"  - Model 2 (処方薬): 検出力 ≈ {results_posthoc['Model 2 (Diabetes_Prescription_Per100k)']['power']:.1%}",
        "",
        "  推奨の論文記載文（Methodsセクション）:",
        "  -------------------------------------------------------",
        "  Statistical power was estimated post-hoc using G*Power",
        "  (or statsmodels). With N=47, k=5 predictors, and the",
        f"  observed R2 of {R2_MODEL1:.3f} (Model 1) and {R2_MODEL2:.3f} (Model 2),",
        f"  the achieved power was {results_posthoc['Model 1 (HbA1c_Mean)']['power']:.1%} and",
        f"  {results_posthoc['Model 2 (Diabetes_Prescription_Per100k)']['power']:.1%}, respectively.",
        "  To achieve 80% power for a medium effect (f2=0.15),",
        f"  approximately N={required_ns['medium']['n_required']} prefectures would be required,",
        "  which exceeds the number of Japanese prefectures (47).",
        "  These findings should be interpreted with caution given",
        "  the limited statistical power.",
        "  -------------------------------------------------------",
        "",
        "  Limitationsでの記載ポイント:",
        "  - N=47 は固定（日本の都道府県数）であり増加不可",
        f"  - medium効果量で80%検出力達成には N={required_ns['medium']['n_required']} 必要だが実現不可",
        "  - 「関連なし」という結論には Type II error（偽陰性）のリスクがある",
        "  - より細かい地理的単位（二次医療圏 N≈335）や",
        "    個人レベルコホート研究が理想的",
        "",
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    logger.info(f"検出力分析結果を保存: {output_file.name}")

    # ============================
    # 4. 検出力曲線プロット
    # ============================
    fig_path = FIGURES_DIR / 'power_curve.png'
    plot_power_curves(K_VARS, ALPHA, fig_path)

    # ============================
    # コンソールサマリー
    # ============================
    print("\n" + "=" * 60)
    print("Phase 6d 統計的検出力分析 完了")
    print("=" * 60)
    for label, res in results_posthoc.items():
        print(f"  {label}: power = {res['power']:.1%} (f2={res['f2']:.4f})")
    print(f"\n  medium効果量(f2=0.15)で80%検出力に必要なN: {required_ns['medium']['n_required']}")
    print(f"\n  出力ファイル:")
    print(f"    - {output_file}")
    print(f"    - {fig_path}")

    logger.info("Phase 6d 完了")


if __name__ == '__main__':
    main()
