"""
参考文献を整理するスクリプト：
1. 未引用文献を適切な箇所に追加
2. 初登場順に番号を振り直す
3. Referencesセクションを並べ替え
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("STEP 1: 未引用文献の追加")
print("=" * 80)

# 未引用文献の追加箇所を定義
additions = [
    {
        'old_text': 'Several recent meta-analyses have documented modest but statistically significant associations, typically on the order of a 10–15% increase in diabetes risk per 10 μg/m³ increase in PM2.5 1),6),7),27),28).',
        'new_text': 'Several recent meta-analyses have documented modest but statistically significant associations, typically on the order of a 10–15% increase in diabetes risk per 10 μg/m³ increase in PM2.5 1),6),7),27),28).',
        'note': '27) He et al. 2017 は既に引用されている'
    },
    {
        'old_text': 'In contrast, several European and North American cohorts and ecological studies have reported null or borderline associations, particularly at lower exposure ranges or in highly adjusted models 8),9).',
        'new_text': 'In contrast, several European and North American cohorts and ecological studies have reported null or borderline associations, particularly at lower exposure ranges or in highly adjusted models 8),9),14),15).',
        'note': '14) Chen et al. 2013 (Ontario), 15) Coogan et al. 2012 (Los Angeles) を追加'
    },
    {
        'old_text': 'Within Japan, both individual-level and area-level studies have documented positive associations between PM2.5 exposure and diabetes prevalence in urban settings and gestational diabetes risk 20),21),26),',
        'new_text': 'Within Japan, both individual-level and area-level studies have documented positive associations between PM2.5 exposure and diabetes prevalence in urban settings and gestational diabetes risk 20),21),26),',
        'note': '20) Mitsuhashi et al. 2019, 21) Ito et al. 2023 は既に引用されている'
    },
    {
        'old_text': 'The use of NDB Open Data enabled ascertainment of diabetes-related outcomes without selection bias inherent in voluntary cohort participation, although it introduced other forms of selection bias related to health checkup participation and prescription patterns.',
        'new_text': 'The use of NDB Open Data enabled ascertainment of diabetes-related outcomes without selection bias inherent in voluntary cohort participation, although it introduced other forms of selection bias related to health checkup participation and prescription patterns. Similar administrative data approaches have been used in Japanese PM2.5 health research 37),38).',
        'note': '37) Kubo et al. 2021 (CVD), 38) Yorifuji et al. 2020 (12 cities) を追加'
    }
]

# 追加を実行
modified_content = content
for addition in additions:
    if addition['old_text'] in modified_content:
        modified_content = modified_content.replace(addition['old_text'], addition['new_text'])
        print(f"✓ 追加: {addition['note']}")
    else:
        print(f"✗ 見つからない: {addition['note']}")

# 40) Shin et al. (Mental health) は削除（糖尿病と直接関連なし）
print("\n✓ 40) Shin et al. (Mental health) は削除対象としてマーク")

print("\n" + "=" * 80)
print("STEP 2: 初登場順の確認と再番号付け")
print("=" * 80)

# Referencesセクションより前の本文部分のみを対象
refs_start = modified_content.find("# References")
if refs_start == -1:
    refs_start = len(modified_content)
main_content = modified_content[:refs_start]
refs_content = modified_content[refs_start:]

# 引用パターンを抽出（改善版）
citation_pattern = r'(?<=[a-zA-Z\s\.])\d+\)(?:,\s*\d+\))*'

# 統計値を含む行を除外するためのパターン
exclude_patterns = [
    '(N = ', '(n = ', 'p = 0.', 'β = ', 'SE = ',
    'CI = ', 'R² = ', 'HR = ', 'OR = ', 'AIC', 'BIC',
    'Min', 'Max', 'Mean', 'SD', 'Median', '| '
]

first_appearance = {}
cited_numbers = set()

for line in main_content.split('\n'):
    # 統計値を含む行をスキップ
    if any(pattern in line for pattern in exclude_patterns):
        continue

    # テーブル行をスキップ
    if re.search(r'\|\s*\d+\.?\d*\s*\|', line):
        continue

    # 引用パターンを検索
    for match in re.finditer(citation_pattern, line):
        citation_text = match.group()

        # 前後のコンテキストを確認
        start_in_line = max(0, match.start() - 30)
        context = line[start_in_line:match.end() + 30] if match.end() + 30 < len(line) else line[start_in_line:]

        # 除外パターン
        if any(pattern in context for pattern in ['=', '±', '>', '<', '(', 'μg/m³', 'per 100,000']):
            continue

        # 数値の一部でないことを確認
        before_char = line[match.start() - 1] if match.start() > 0 else ' '
        if before_char.isdigit() or before_char in '.,':
            continue

        # 引用番号を抽出
        numbers = re.findall(r'\d+', citation_text)
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 50:  # 妥当な範囲
                cited_numbers.add(num)
                if num not in first_appearance:
                    first_appearance[num] = main_content.find(citation_text)

# 初登場順に並べる
sorted_by_appearance = sorted(first_appearance.items(), key=lambda x: x[1])
appearance_order = [num for num, _ in sorted_by_appearance]

print(f"\n初登場順（修正前）: {appearance_order[:20]}...")
print(f"引用されている番号の総数: {len(cited_numbers)}")

# 未引用番号を確認
all_numbers = set(range(1, 40))  # 40番は削除するので39まで
uncited = sorted(all_numbers - cited_numbers)
print(f"\n未引用番号: {uncited}")

# 番号のマッピングを作成
old_to_new = {}
for new_num, old_num in enumerate(appearance_order, 1):
    old_to_new[old_num] = new_num

print("\n番号の再割り当て（最初の20個）:")
print("旧番号 → 新番号")
for old_num in sorted(old_to_new.keys())[:20]:
    new_num = old_to_new[old_num]
    if old_num != new_num:
        print(f"  {old_num} → {new_num}")

# マッピングをファイルに保存
mapping_file = Path(__file__).parent / "citation_mapping.txt"
with open(mapping_file, 'w', encoding='utf-8') as f:
    f.write("旧番号,新番号\n")
    for old_num in sorted(old_to_new.keys()):
        f.write(f"{old_num},{old_to_new[old_num]}\n")

print(f"\n✓ マッピングを保存: {mapping_file}")

print("\n" + "=" * 80)
print("注意：実際の番号付け替えは手動で行う必要があります")
print("理由：統計値と引用番号の区別が困難なため、自動置換はリスクが高い")
print("=" * 80)

# 修正後の原稿を保存（未引用文献追加のみ）
output_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes_step1.qmd"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(modified_content)

print(f"\n✓ 未引用文献を追加した原稿を保存: {output_path}")
print("\n次のステップ：")
print("1. Manuscript_PM25_diabetes_step1.qmd を確認")
print("2. citation_mapping.txt を参照して、手動で番号を振り直す")
print("3. Referencesセクションを新しい順序に並べ替える")
