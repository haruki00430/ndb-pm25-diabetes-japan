#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 7: 最終レポート・追加可視化の生成
======================================
本スクリプトは Phase 6d までの解析結果（統合データセットと回帰結果）を踏まえ、
論文化に必要な図表とサマリーレポートを自動生成します。

入力:
  - data/interim/analysis_dataset.csv
  - config/config.yaml

出力:
  - results/figures/
      - choropleth_pm25.png (任意: GeoJSONがある場合のみ)
      - choropleth_hba1c.png (任意)
      - choropleth_dm_rx.png (任意)
      - scatter_pm25_hba1c.png
      - scatter_pm25_dm_rx.png
      - diagnostics_hba1c.png
      - diagnostics_dm_rx.png
      - stations_by_prefecture.png
  - results/reports/
      - table1_top_bottom.csv
      - model_inputs.csv
      - final_summary_report.md

注意:
  - `02_Data/master/japan_prefectures.geojson` が存在しない場合、choroplethはスキップします。
  - GeoPandas が未インストールの場合もchoroplethはスキップします。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yaml

import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy import stats

# ndb_library imports (フォールバックでsrc追加)
try:
    from ndb_library.logger import setup_logger
    from ndb_library.viz import set_japanese_font
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))
    from ndb_library.logger import setup_logger
    from ndb_library.viz import set_japanese_font


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_DIR / "data" / "interim" / "analysis_dataset.csv"
CONFIG_PATH = PROJECT_DIR / "config" / "config.yaml"
RESULTS_DIR = PROJECT_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

_script_dir = Path(__file__).resolve().parent
_log_dir = _script_dir / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "07_final_report.log"
logger = setup_logger(__name__, log_file=str(_log_file))


@dataclass(frozen=True)
class ModelSpec:
    """回帰モデル仕様を表します。"""

    name: str
    y: str
    x: list[str]
    figure_prefix: str


def load_config(path: Path) -> dict:
    """YAML設定を読み込みます。"""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_output_dirs() -> None:
    """出力先ディレクトリを作成します。"""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_analysis_dataset(path: Path) -> pd.DataFrame:
    """統合データセットを読み込みます。"""
    if not path.exists():
        raise FileNotFoundError(f"analysis dataset が見つかりません: {path}")
    df = pd.read_csv(path, dtype={"prefecture_code": str})
    if "prefecture_code" in df.columns:
        df["prefecture_code"] = df["prefecture_code"].astype(str).str.zfill(2)
    return df


def pick_covariates_for_phase7(df: pd.DataFrame) -> list[str]:
    """
    Phase 7 で使用する共変量セットを決定します。

    方針:
      - Phase 6c と整合させ、Smoking_Rate は除外（強い共線性のため）
      - exposure は常に PM25_Mean を含める
    """
    base = ["PM25_Mean"]
    covariates = ["Aging_Rate", "Obesity_Rate", "Exercise_Rate", "GDP_Per_Capita"]
    missing = [c for c in base + covariates if c not in df.columns]
    if missing:
        raise KeyError(f"必要カラムが不足しています: {missing}")
    return base + covariates


def fit_ols(df: pd.DataFrame, y: str, x: list[str]) -> sm.regression.linear_model.RegressionResultsWrapper:
    """OLSを推定します（欠損は行単位で除外）。"""
    df_clean = df[[y] + x].dropna()
    y_vec = df_clean[y].to_numpy()
    X = sm.add_constant(df_clean[x].to_numpy())
    model = sm.OLS(y_vec, X)
    return model.fit()


def save_scatter_with_ci(
    df: pd.DataFrame,
    x: str,
    y: str,
    xlabel: str,
    ylabel: str,
    title: str,
    out_path: Path,
) -> None:
    """Scatter plot with OLS regression line and 95% CI."""
    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    sns.regplot(
        data=df,
        x=x,
        y=y,
        ci=95,
        scatter_kws={"s": 55, "alpha": 0.75, "edgecolor": "k", "linewidths": 0.4},
        line_kws={"color": "crimson", "linewidth": 2.0},
        ax=ax,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_diagnostics_4panel(
    results: sm.regression.linear_model.RegressionResultsWrapper,
    model_title: str,
    out_path: Path,
) -> None:
    """残差診断の4パネル図を保存します。"""
    set_japanese_font()
    sns.set_style("whitegrid")

    resid = results.resid
    fitted = results.fittedvalues
    influence = results.get_influence()
    standardized_resid = influence.resid_studentized_internal
    leverage = influence.hat_matrix_diag
    cooks = influence.cooks_distance[0]

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 9.0))
    ax1, ax2, ax3, ax4 = axes.flatten()

    # (A) Residuals vs Fitted
    ax1.scatter(fitted, resid, s=45, alpha=0.75, edgecolor="k", linewidth=0.35)
    ax1.axhline(0, color="crimson", linewidth=1.4, linestyle="--")
    ax1.set_title("Residuals vs Fitted", fontweight="bold")
    ax1.set_xlabel("Fitted values")
    ax1.set_ylabel("Residuals")

    # (B) Q-Q plot
    sm.qqplot(resid, line="45", ax=ax2, markerfacecolor="steelblue", markeredgecolor="k", alpha=0.75)
    ax2.set_title("Normal Q-Q", fontweight="bold")

    # (C) Scale-Location
    ax3.scatter(fitted, np.sqrt(np.abs(standardized_resid)), s=45, alpha=0.75, edgecolor="k", linewidth=0.35)
    ax3.set_title("Scale-Location", fontweight="bold")
    ax3.set_xlabel("Fitted values")
    ax3.set_ylabel("Sqrt(|Standardized residuals|)")

    # (D) Residuals vs Leverage (Cook's distance)
    ax4.scatter(leverage, standardized_resid, s=45, alpha=0.75, edgecolor="k", linewidth=0.35)
    ax4.axhline(0, color="crimson", linewidth=1.2, linestyle="--")
    ax4.set_title("Residuals vs Leverage", fontweight="bold")
    ax4.set_xlabel("Leverage")
    ax4.set_ylabel("Standardized residuals")

    # Cook's distanceの大きい点を軽く強調
    if len(cooks) == len(leverage):
        idx = np.argsort(cooks)[-3:]
        for i in idx:
            ax4.annotate(str(i + 1), (leverage[i], standardized_resid[i]), fontsize=9)

    fig.suptitle(model_title, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


_PREF_ROMAJI = {
    '北海道': 'Hokkaido', '青森': 'Aomori', '岩手': 'Iwate', '宮城': 'Miyagi',
    '秋田': 'Akita', '山形': 'Yamagata', '福島': 'Fukushima', '茨城': 'Ibaraki',
    '栃木': 'Tochigi', '群馬': 'Gunma', '埼玉': 'Saitama', '千葉': 'Chiba',
    '東京': 'Tokyo', '神奈川': 'Kanagawa', '新潟': 'Niigata', '富山': 'Toyama',
    '石川': 'Ishikawa', '福井': 'Fukui', '山梨': 'Yamanashi', '長野': 'Nagano',
    '岐阜': 'Gifu', '静岡': 'Shizuoka', '愛知': 'Aichi', '三重': 'Mie',
    '滋賀': 'Shiga', '京都': 'Kyoto', '大阪': 'Osaka', '兵庫': 'Hyogo',
    '奈良': 'Nara', '和歌山': 'Wakayama', '鳥取': 'Tottori', '島根': 'Shimane',
    '岡山': 'Okayama', '広島': 'Hiroshima', '山口': 'Yamaguchi', '徳島': 'Tokushima',
    '香川': 'Kagawa', '愛媛': 'Ehime', '高知': 'Kochi', '福岡': 'Fukuoka',
    '佐賀': 'Saga', '長崎': 'Nagasaki', '熊本': 'Kumamoto', '大分': 'Oita',
    '宮崎': 'Miyazaki', '鹿児島': 'Kagoshima', '沖縄': 'Okinawa',
}


def _to_romaji(name: str) -> str:
    """日本語都道府県名をローマ字に変換します。"""
    if name in _PREF_ROMAJI:
        return _PREF_ROMAJI[name]
    for suffix in ('県', '都', '道', '府'):
        stripped = name.replace(suffix, '')
        if stripped in _PREF_ROMAJI:
            return _PREF_ROMAJI[stripped]
    return name


def save_stations_plot(df: pd.DataFrame, out_path: Path) -> None:
    """PM2.5 monitoring station counts by prefecture."""
    sns.set_style("whitegrid")

    if "PM25_N_Stations" not in df.columns:
        logger.warning("PM25_N_Stations がないため stations 図をスキップします。")
        return

    plot_df = df[["prefecture_name", "PM25_N_Stations"]].copy()
    plot_df["prefecture_en"] = plot_df["prefecture_name"].map(_to_romaji)
    plot_df = plot_df.sort_values("PM25_N_Stations", ascending=False)

    fig, ax = plt.subplots(figsize=(10.5, 9.5))
    ax.barh(plot_df["prefecture_en"], plot_df["PM25_N_Stations"], color="slategray", edgecolor="black", linewidth=0.3)
    ax.invert_yaxis()
    ax.set_xlabel("Number of PM2.5 monitoring stations")
    ax.set_ylabel("Prefecture")
    ax.set_title("PM2.5 Monitoring Stations by Prefecture (N = 47)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def try_import_geopandas():
    """GeoPandasを任意依存としてimportします。"""
    try:
        import geopandas as gpd  # type: ignore
    except Exception:
        return None
    return gpd


def save_choropleth_if_available(
    df: pd.DataFrame,
    geojson_path: Path,
    value_col: str,
    title: str,
    out_path: Path,
    cmap: str = "viridis",
) -> bool:
    """
    GeoJSON と GeoPandas が利用可能な場合のみ choropleth を生成します。
    戻り値: 生成できたら True。
    """
    gpd = try_import_geopandas()
    if gpd is None:
        logger.warning("GeoPandas が利用できないため、choropleth をスキップします。")
        return False

    if not geojson_path.exists():
        logger.warning(f"GeoJSON が見つからないため、choropleth をスキップします: {geojson_path}")
        return False

    set_japanese_font()
    geo = gpd.read_file(geojson_path)

    # 列名の揺れに対応（一般的な 'prefecture' / 'name' / 'prefecture_name' を試す）
    name_candidates = ["prefecture_name", "prefecture", "name", "nam_ja", "pref_name"]
    geo_name_col = next((c for c in name_candidates if c in geo.columns), None)
    if geo_name_col is None:
        logger.warning(f"GeoJSON の都道府県名列が特定できません（候補={name_candidates}）。choroplethをスキップします。")
        return False

    merged = geo.merge(df[["prefecture_name", value_col]], left_on=geo_name_col, right_on="prefecture_name", how="left")
    if merged[value_col].isna().all():
        logger.warning("GeoJSON とのマージに失敗（値列が全てNA）。choroplethをスキップします。")
        return False

    fig, ax = plt.subplots(figsize=(7.2, 8.4))
    merged.plot(column=value_col, cmap=cmap, linewidth=0.3, edgecolor="white", legend=True, ax=ax)
    ax.set_axis_off()
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return True


def build_table1_top_bottom(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 1 用の上位/下位10都道府県を作成します。
    """
    targets = [
        ("PM25_Mean", "PM2.5 (μg/m³)"),
        ("HbA1c_Mean", "HbA1c (%)"),
        ("Diabetes_Prescription_Per100k", "糖尿病用剤処方数/10万人"),
    ]
    rows: list[dict] = []
    for col, label in targets:
        if col not in df.columns:
            continue
        tmp = df[["prefecture_code", "prefecture_name", col]].dropna().copy()
        tmp = tmp.sort_values(col, ascending=False)
        top = tmp.head(10)
        bottom = tmp.tail(10).sort_values(col, ascending=True)
        for _, r in top.iterrows():
            rows.append({"indicator": label, "rank_group": "top10", "prefecture": r["prefecture_name"], "value": r[col]})
        for _, r in bottom.iterrows():
            rows.append({"indicator": label, "rank_group": "bottom10", "prefecture": r["prefecture_name"], "value": r[col]})
    return pd.DataFrame(rows)


def write_final_summary(
    df: pd.DataFrame,
    models: Iterable[ModelSpec],
    results_by_name: dict[str, sm.regression.linear_model.RegressionResultsWrapper],
    config: dict,
    outputs: dict[str, str],
    out_path: Path,
) -> None:
    """最終サマリーレポート（Markdown）を生成します。"""
    lines: list[str] = []
    lines.append("# Phase 7: 最終サマリーレポート（自動生成）\n")
    lines.append(f"- 生成日時: {pd.Timestamp.now().isoformat(timespec='seconds')}")
    lines.append(f"- 対象: {config.get('project_id', 'NDB_XXX_PM25_diabetes')}")
    lines.append(f"- サンプル: {len(df)} 都道府県\n")

    lines.append("## 主要結論\n")
    lines.append("- PM2.5 と糖尿病指標（HbA1c平均値、糖尿病用剤処方数/10万人）の関連は、共変量調整後も有意な関連を示さなかった（本データ・本設計の範囲）。")
    lines.append("- 多重共線性（共変量間の強相関）が残存しており、係数推定の不安定性・Type II error（偽陰性）の可能性はLimitationsとして明確化が必要。\n")

    lines.append("## 回帰結果（Phase 7で再推定：縮約モデル整合）\n")
    for m in models:
        res = results_by_name[m.name]
        coef_idx = 1  # const=0, PM25=1
        beta_pm25 = float(res.params[coef_idx])
        se_pm25 = float(res.bse[coef_idx])
        p_pm25 = float(res.pvalues[coef_idx])
        r2 = float(res.rsquared)
        ar2 = float(res.rsquared_adj)
        shapiro_w, shapiro_p = stats.shapiro(res.resid)
        lines.append(f"### {m.name}")
        lines.append(f"- 従属変数: `{m.y}`")
        lines.append(f"- 説明変数: `{', '.join(m.x)}`")
        lines.append(f"- PM2.5係数（β±SE）: {beta_pm25:.6g} ± {se_pm25:.6g}（p={p_pm25:.4g}）")
        lines.append(f"- R² / Adj.R²: {r2:.3f} / {ar2:.3f}")
        lines.append(f"- 残差正規性（Shapiro-Wilk）: W={shapiro_w:.4f}, p={shapiro_p:.4g}\n")

    lines.append("## 生成ファイル\n")
    for k, v in outputs.items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")

    lines.append("## Choropleth について\n")
    if "choropleth_pm25" in outputs:
        lines.append("- GeoJSON が利用可能なため、choropleth を生成しました。")
    else:
        lines.append("- GeoJSON または GeoPandas が利用できないため、choropleth はスキップしました。")
        lines.append("- `02_Data/master/japan_prefectures.geojson` を配置すると自動生成されます。")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    logger.info("=" * 80)
    logger.info("Phase 7: Final report and figures")
    logger.info("=" * 80)

    ensure_output_dirs()
    set_japanese_font()

    config = load_config(CONFIG_PATH)
    df = load_analysis_dataset(DATASET_PATH)

    x_vars = pick_covariates_for_phase7(df)
    models = [
        ModelSpec(
            name="Model 1 (HbA1c)",
            y="HbA1c_Mean",
            x=x_vars,
            figure_prefix="hba1c",
        ),
        ModelSpec(
            name="Model 2 (Diabetes medication)",
            y="Diabetes_Prescription_Per100k",
            x=x_vars,
            figure_prefix="dm_rx",
        ),
    ]

    # 記録用: モデル入力データ（欠損除外後）を保存
    model_input = df[["prefecture_code", "prefecture_name"] + sorted(set([m.y for m in models] + x_vars))].copy()
    model_input_path = REPORTS_DIR / "model_inputs.csv"
    model_input.to_csv(model_input_path, index=False, encoding="utf-8")

    # 図: 散布図（単変量の見せ方）
    scatter1 = FIGURES_DIR / "scatter_pm25_hba1c.png"
    save_scatter_with_ci(
        df=df,
        x="PM25_Mean",
        y="HbA1c_Mean",
        xlabel="Annual mean PM2.5 (μg/m³)",
        ylabel="Mean HbA1c (%)",
        title="PM2.5 vs. Mean HbA1c (47 Japanese Prefectures)",
        out_path=scatter1,
    )

    scatter2 = FIGURES_DIR / "scatter_pm25_dm_rx.png"
    save_scatter_with_ci(
        df=df,
        x="PM25_Mean",
        y="Diabetes_Prescription_Per100k",
        xlabel="Annual mean PM2.5 (μg/m³)",
        ylabel="Diabetes medication prescriptions (per 100,000)",
        title="PM2.5 vs. Diabetes Medication Prescriptions (47 Japanese Prefectures)",
        out_path=scatter2,
    )

    # 図: 測定局数の可視化
    stations_fig = FIGURES_DIR / "stations_by_prefecture.png"
    save_stations_plot(df, stations_fig)

    # 回帰再推定＋診断図
    results_by_name: dict[str, sm.regression.linear_model.RegressionResultsWrapper] = {}
    for m in models:
        res = fit_ols(df, y=m.y, x=m.x)
        results_by_name[m.name] = res
        diag_path = FIGURES_DIR / f"diagnostics_{m.figure_prefix}.png"
        save_diagnostics_4panel(res, model_title=m.name, out_path=diag_path)

    # Table 1 (top/bottom)
    table1 = build_table1_top_bottom(df)
    table1_path = REPORTS_DIR / "table1_top_bottom.csv"
    table1.to_csv(table1_path, index=False, encoding="utf-8-sig")

    # Choropleth (任意)
    geojson_rel = config.get("visualization", {}).get("prefecture_geojson", "02_Data/master/japan_prefectures.geojson")
    geojson_path = Path(__file__).resolve().parents[3] / str(geojson_rel)
    choropleths: dict[str, str] = {}
    if save_choropleth_if_available(
        df=df,
        geojson_path=geojson_path,
        value_col="PM25_Mean",
        title="PM2.5 年平均濃度（都道府県別）",
        out_path=FIGURES_DIR / "choropleth_pm25.png",
        cmap=config.get("visualization", {}).get("color_scheme", "viridis"),
    ):
        choropleths["choropleth_pm25"] = str((FIGURES_DIR / "choropleth_pm25.png").as_posix())
    if save_choropleth_if_available(
        df=df,
        geojson_path=geojson_path,
        value_col="HbA1c_Mean",
        title="HbA1c 平均値（都道府県別）",
        out_path=FIGURES_DIR / "choropleth_hba1c.png",
        cmap=config.get("visualization", {}).get("color_scheme", "viridis"),
    ):
        choropleths["choropleth_hba1c"] = str((FIGURES_DIR / "choropleth_hba1c.png").as_posix())
    if save_choropleth_if_available(
        df=df,
        geojson_path=geojson_path,
        value_col="Diabetes_Prescription_Per100k",
        title="糖尿病用剤 処方数/10万人（都道府県別）",
        out_path=FIGURES_DIR / "choropleth_dm_rx.png",
        cmap=config.get("visualization", {}).get("color_scheme", "viridis"),
    ):
        choropleths["choropleth_dm_rx"] = str((FIGURES_DIR / "choropleth_dm_rx.png").as_posix())

    # Summary report
    outputs: dict[str, str] = {
        "scatter_pm25_hba1c": str(scatter1.as_posix()),
        "scatter_pm25_dm_rx": str(scatter2.as_posix()),
        "diagnostics_hba1c": str((FIGURES_DIR / "diagnostics_hba1c.png").as_posix()),
        "diagnostics_dm_rx": str((FIGURES_DIR / "diagnostics_dm_rx.png").as_posix()),
        "stations_by_prefecture": str(stations_fig.as_posix()),
        "table1_top_bottom": str(table1_path.as_posix()),
        "model_inputs": str(model_input_path.as_posix()),
    }
    outputs.update(choropleths)

    summary_path = REPORTS_DIR / "final_summary_report.md"
    write_final_summary(
        df=df,
        models=models,
        results_by_name=results_by_name,
        config=config,
        outputs=outputs,
        out_path=summary_path,
    )

    logger.info("Phase 7 completed.")
    logger.info(f"Figures: {FIGURES_DIR}")
    logger.info(f"Reports: {REPORTS_DIR}")


if __name__ == "__main__":
    main()

