"""
未引用文献をプレースホルダ形式で追加するスクリプト
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# プレースホルダ版の原稿を読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes_placeholder.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("未引用文献の追加")
print("=" * 80)

# 追加する文献と追加箇所を定義
additions = [
    {
        'old_text': 'In contrast, several European and North American cohorts and ecological studies have reported null or borderline associations, particularly at lower exposure ranges or in highly adjusted models ##REF_8##,##REF_9##.',
        'new_text': 'In contrast, several European and North American cohorts and ecological studies have reported null or borderline associations, particularly at lower exposure ranges or in highly adjusted models ##REF_8##,##REF_9##,##REF_14##,##REF_15##.',
        'added': '14) Chen et al. 2013 (Ontario), 15) Coogan et al. 2012 (Los Angeles)',
        'note': 'Section 2: 北米の研究として追加'
    },
    {
        'old_text': 'Within Japan, both individual-level and area-level studies have documented positive associations between PM2.5 exposure and diabetes prevalence in urban settings and gestational diabetes risk ##REF_20##,##REF_21##,##REF_26##,',
        'new_text': 'Within Japan, both individual-level and area-level studies have documented positive associations between PM2.5 exposure and diabetes prevalence in urban settings and gestational diabetes risk ##REF_20##,##REF_21##,##REF_26##,',
        'added': '20) Mitsuhashi et al. 2019, 21) Ito et al. 2023 (既に引用されている)',
        'note': 'Section 2: 日本の研究（既に引用済み）'
    },
    {
        'old_text': 'The use of NDB Open Data enabled ascertainment of diabetes-related outcomes without selection bias inherent in voluntary cohort participation, although it introduced other forms of selection bias related to health checkup participation and prescription patterns.',
        'new_text': 'The use of NDB Open Data enabled ascertainment of diabetes-related outcomes without selection bias inherent in voluntary cohort participation, although it introduced other forms of selection bias related to health checkup participation and prescription patterns. Similar administrative data approaches have been successfully used in Japanese PM2.5 health research ##REF_37##,##REF_38##.',
        'added': '37) Kubo et al. 2021 (CVD), 38) Yorifuji et al. 2020 (12 cities)',
        'note': 'Section 5 (Strengths): 日本のPM2.5研究として追加'
    },
]

# 40) Shin et al. (Mental health) は削除（糖尿病と直接関連なし）
print("注意: 40) Shin et al. (Mental health) は糖尿病との直接的な関連性が低いため、追加しません\n")

modified_content = content
added_count = 0

for addition in additions:
    if addition['old_text'] in modified_content:
        modified_content = modified_content.replace(addition['old_text'], addition['new_text'])
        added_count += 1
        print(f"✓ 追加: {addition['added']}")
        print(f"  {addition['note']}\n")
    else:
        print(f"✗ 見つからない: {addition['note']}")
        print(f"  探索テキスト: {addition['old_text'][:80]}...\n")

print(f"合計 {added_count} 箇所に文献を追加しました")

# 追加後のプレースホルダを確認
placeholder_pattern = r'##REF_(\d+)##'
found_refs = set()
for match in re.finditer(placeholder_pattern, modified_content):
    found_refs.add(int(match.group(1)))

print(f"\n検出されたプレースホルダ（追加後）: {sorted(found_refs)}")
print(f"総数: {len(found_refs)}")

# 未追加の文献
expected_refs = set(range(1, 40))  # 1-39（40は除外）
missing_refs = sorted(expected_refs - found_refs)
if missing_refs:
    print(f"\n⚠️ まだ追加されていない文献: {missing_refs}")

# 修正版を保存
output_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes_placeholder_v2.qmd"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(modified_content)

print(f"\n✓ 未引用文献を追加した版を保存: {output_path}")

print("\n" + "=" * 80)
print("次のステップ: 初登場順にプレースホルダを並べ替え")
print("=" * 80)

# 初登場順を検出
refs_start = modified_content.find("# References")
main_content = modified_content[:refs_start] if refs_start != -1 else modified_content

first_appearance = {}
current_pos = 0
for match in re.finditer(placeholder_pattern, main_content):
    ref_num = int(match.group(1))
    if ref_num not in first_appearance:
        first_appearance[ref_num] = current_pos + match.start()
    current_pos = match.end()

# 初登場順に並べる
sorted_refs = sorted(first_appearance.items(), key=lambda x: x[1])
appearance_order = [ref_num for ref_num, _ in sorted_refs]

print(f"\n初登場順: {appearance_order}")
print(f"\n理想的な順序（1から順番）: {list(range(1, len(appearance_order) + 1))}")

# マッピングを作成
old_to_new = {}
for new_num, old_num in enumerate(appearance_order, 1):
    old_to_new[old_num] = new_num

if appearance_order == list(range(1, len(appearance_order) + 1)):
    print("\n✓ すでに初登場順に並んでいます！")
else:
    print("\n✗ 並べ替えが必要です")
    print("\n変更が必要な番号（最初の15個）:")
    print("旧番号 → 新番号")
    changes_shown = 0
    for old_num in sorted(old_to_new.keys()):
        new_num = old_to_new[old_num]
        if old_num != new_num:
            print(f"  ##REF_{old_num}## → {new_num})")
            changes_shown += 1
            if changes_shown >= 15:
                print("  ...")
                break

    # マッピングをファイルに保存
    mapping_file = Path(__file__).parent / "ref_mapping_final.txt"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        f.write("旧番号,新番号\n")
        for old_num in sorted(old_to_new.keys()):
            f.write(f"{old_num},{old_to_new[old_num]}\n")

    print(f"\n✓ 完全なマッピングを保存: {mapping_file}")
