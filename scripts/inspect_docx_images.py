#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
09Manuscript DOCX内の埋め込み画像を検査して情報を出力する。
"""
import sys
import zipfile
from pathlib import Path
import shutil

DOCX_PATH = Path(__file__).resolve().parents[1] / "04_Manuscripts" / "09Manuscript_PM25_diabetes_references_final.docx"
EXTRACT_DIR = Path(__file__).resolve().parents[1] / "04_Manuscripts" / "_docx_images_inspect"


def inspect(docx_path: Path, extract_dir: Path) -> None:
    if not docx_path.exists():
        print(f"[ERROR] DOCX not found: {docx_path}")
        sys.exit(1)

    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)

    # DOCX は ZIP なので展開して画像を取り出す
    with zipfile.ZipFile(docx_path, "r") as zf:
        names = zf.namelist()
        media = [n for n in names if n.startswith("word/media/")]
        print(f"Total files in DOCX: {len(names)}")
        print(f"Media files: {len(media)}")
        print()
        for m in sorted(media):
            info = zf.getinfo(m)
            fname = Path(m).name
            print(f"  {fname:40s}  {info.file_size:>10,} bytes")
            zf.extract(m, extract_dir)

    print(f"\nImages extracted to: {extract_dir / 'word' / 'media'}")


if __name__ == "__main__":
    inspect(DOCX_PATH, EXTRACT_DIR)
