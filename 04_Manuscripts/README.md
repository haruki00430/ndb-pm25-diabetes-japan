# 04_Manuscripts（原稿フォルダ）

このフォルダは、`projects/NDB_XXX_PM25_diabetes` プロジェクトの論文化（Quarto原稿）用です。

## ステータス（2026-04-05 リポジトリ照合）

- 正本は下記「Canonical 原稿」。`obsidian_vault/20_Projects/NDB_XXX_PM25_diabetes.md` と一致。

## Canonical 原稿（正本）

**運用上の正本**: `Manuscript_PM25_diabetes.qmd`（`obsidian_vault/20_Projects/` のダッシュボード・Obsidian Citations の切替と一致させる）。

別バージョン（`_final`、`_placeholder` 等）は試行用。正本を変える場合は本節とダッシュボードを同時に更新すること。

## ファイル

- `Manuscript_PM25_diabetes.qmd`: **Canonical**（下記 `quarto render` 例）
- `Manuscript_PM25_diabetes_final.qmd` 等: 試行・版管理用。正本の変更時は上記「Canonical 原稿」を更新すること。
- `manuscript.qmd`: 原稿雛形（IMRAD + STROBE観点の項目）
- `references.bib`: 参考文献

## 図表の生成

Phase 7の図表・サマリーレポートは、プロジェクトルートから以下で生成します。

```bash
cd projects/NDB_XXX_PM25_diabetes
python analysis/07_final_report.py
```

生成物:

- `../results/figures/*.png`
- `../results/reports/final_summary_report.md`

## 原稿のレンダリング（HTML/DOCX）

```bash
quarto render projects/NDB_XXX_PM25_diabetes/04_Manuscripts/Manuscript_PM25_diabetes.qmd --to html
quarto render projects/NDB_XXX_PM25_diabetes/04_Manuscripts/Manuscript_PM25_diabetes.qmd --to docx
```

## 注意

- choropleth は `02_Data/master/japan_prefectures.geojson` が存在し、かつ GeoPandas が利用可能な場合にのみ生成されます。

