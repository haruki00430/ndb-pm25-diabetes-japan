"""
PM25_diabetes.qmdのPythonコードブロックを静的テーブルに置き換え
"""
import re
from pathlib import Path
import sys

# UTF-8出力を強制
sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 静的テーブルを読み込み
static_tables_path = Path(__file__).parent / "static_tables_output.md"
with open(static_tables_path, 'r', encoding='utf-8') as f:
    static_content = f.read()

# 各テーブルを抽出
table1_match = re.search(r'# Table 1: Descriptive Statistics\n\n(.*?)\n\n---', static_content, re.DOTALL)
table2_match = re.search(r'# Table 2: Multivariable OLS Regression Results\n\n(.*?)\n\n---', static_content, re.DOTALL)
table3_match = re.search(r'# Table 3: Sensitivity Analyses.*?\n\n(.*?)\n\n完了', static_content, re.DOTALL)

if not all([table1_match, table2_match, table3_match]):
    print("Error: Could not extract all tables")
    exit(1)

table1_md = table1_match.group(1).strip()
table2_md = table2_match.group(1).strip()
table3_md = table3_match.group(1).strip()

# Table 1のPythonコードブロックを置換
pattern1 = r'(## Table 1\. Descriptive Statistics of Prefecture-Level Variables \(N = 47\)\n\n)```\{python\}.*?```'
replacement1 = r'\1' + table1_md
content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

# Table 2のPythonコードブロックを置換
pattern2 = r'(## Table 2\. Multivariable OLS Regression Results \(N = 47\)\n\n)```\{python\}.*?```'
replacement2 = r'\1' + table2_md
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

# Table 3のPythonコードブロックを置換
pattern3 = r'(## Table 3\. Sensitivity Analyses \(PM2\.5 coefficient\)\n\n)```\{python\}.*?```'
replacement3 = r'\1' + table3_md
content = re.sub(pattern3, replacement3, content, flags=re.DOTALL)

# 変換後のファイルを保存
with open(manuscript_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Pythonコードブロックを静的テーブルに置き換えました: {manuscript_path}")
print(f"  - Table 1: {len(table1_md)} chars")
print(f"  - Table 2: {len(table2_md)} chars")
print(f"  - Table 3: {len(table3_md)} chars")
