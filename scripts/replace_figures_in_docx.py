#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
09Manuscript_PM25_diabetes_references_final.docx 内の日本語ガーベージ画像を
英語化済みの新しい図に置換して最終 DOCX を出力する。

置換マッピング（DOCX内 word/media/ ファイル名 → 新しい図のパス）:
  image2.png  → results/figures/scatter_pm25_hba1c.png
  image3.png  → results/figures/scatter_pm25_dm_rx.png
  image6.png  → results/figures/stations_by_prefecture.png

置換しない（既に英語で問題なし）:
  image1.png  → 別エージェント追加の概念図
  image4.png  → diagnostics_hba1c.png（英語ラベル）
  image5.png  → diagnostics_dm_rx.png（英語ラベル）

出力: 04_Manuscripts/10Manuscript_PM25_diabetes_figures_en.docx
"""
import shutil
import zipfile
from pathlib import Path

# --- パス定義 ---
MANUSCRIPTS_DIR = Path(__file__).resolve().parents[1] / "04_Manuscripts"
FIGURES_DIR = Path(__file__).resolve().parents[1] / "results" / "figures"

SRC_DOCX  = MANUSCRIPTS_DIR / "09Manuscript_PM25_diabetes_references_final.docx"
DST_DOCX  = MANUSCRIPTS_DIR / "10Manuscript_PM25_diabetes_figures_en.docx"

# DOCX内のメディア名 → 置換する新しい図ファイル
REPLACE_MAP: dict[str, Path] = {
    "image2.png": FIGURES_DIR / "scatter_pm25_hba1c.png",
    "image3.png": FIGURES_DIR / "scatter_pm25_dm_rx.png",
    "image6.png": FIGURES_DIR / "stations_by_prefecture.png",
}


def replace_images(src: Path, dst: Path, replace_map: dict[str, Path]) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Source DOCX not found: {src}")

    for src_name, new_fig in replace_map.items():
        if not new_fig.exists():
            raise FileNotFoundError(f"New figure not found: {new_fig}")

    # 元の DOCX をコピーして作業ファイルを作成
    shutil.copy2(src, dst)
    print(f"Copied {src.name} -> {dst.name}")

    # ZIP を更新（既存エントリを上書き）
    with zipfile.ZipFile(dst, "a") as zf:
        for src_name, new_fig in replace_map.items():
            arcname = f"word/media/{src_name}"
            # 既存エントリを削除してから新たに追加
            # zipfile モジュールは直接削除できないため、
            # 一時ファイルを用いて書き直す方式をとる
            pass  # 後の処理で対応

    # ZIP の中身を書き直す（削除 + 追加対応）
    tmp = dst.with_suffix(".tmp.docx")
    with zipfile.ZipFile(dst, "r") as zin, zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            fname = item.filename
            media_name = Path(fname).name  # e.g. "image2.png"

            if fname.startswith("word/media/") and media_name in replace_map:
                new_fig = replace_map[media_name]
                new_data = new_fig.read_bytes()
                zout.writestr(item, new_data)
                print(f"  Replaced: {fname} <- {new_fig.name}  ({len(new_data):,} bytes)")
            else:
                zout.writestr(item, zin.read(item.filename))

    # 一時ファイルで上書き
    shutil.move(str(tmp), str(dst))
    print(f"\nOutput: {dst}")


if __name__ == "__main__":
    replace_images(SRC_DOCX, DST_DOCX, REPLACE_MAP)
    print("Done.")
