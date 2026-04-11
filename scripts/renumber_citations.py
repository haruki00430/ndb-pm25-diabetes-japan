"""
プレースホルダを初登場順の番号に置換するスクリプト
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# マッピングファイルを読み込み
mapping_file = Path(__file__).parent / "ref_mapping_final.txt"
old_to_new = {}

with open(mapping_file, 'r', encoding='utf-8') as f:
    next(f)  # ヘッダーをスキップ
    for line in f:
        if line.strip():
            old_num, new_num = map(int, line.strip().split(','))
            old_to_new[old_num] = new_num

print("=" * 80)
print("プレースホルダを新番号に置換")
print("=" * 80)

# プレースホルダ版v2を読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes_placeholder_v2.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Referencesセクションを分離
refs_start = content.find("# References")
main_content = content[:refs_start]
refs_content = content[refs_start:]

# プレースホルダを新番号に置換
# 重要：降順で置換（大きい番号から順に）して、既に置換した番号との混同を避ける
modified_content = main_content

for old_num in sorted(old_to_new.keys(), reverse=True):
    new_num = old_to_new[old_num]
    old_placeholder = f"##REF_{old_num}##"
    new_citation = f"{new_num})"

    # 置換回数をカウント
    count = modified_content.count(old_placeholder)
    if count > 0:
        modified_content = modified_content.replace(old_placeholder, new_citation)
        if old_num != new_num:
            print(f"✓ ##REF_{old_num}## → {new_num}) ({count} 箇所)")

# 念のため、残っているプレースホルダがないか確認
remaining_placeholders = re.findall(r'##REF_\d+##', modified_content)
if remaining_placeholders:
    print(f"\n⚠️ 警告: 置換されなかったプレースホルダがあります: {set(remaining_placeholders)}")
else:
    print("\n✓ 全てのプレースホルダを置換しました")

# Referencesセクションを並べ替え
print("\n" + "=" * 80)
print("Referencesセクションの並べ替え")
print("=" * 80)

# 現在のReferencesセクションから各文献を抽出
ref_pattern = r'^(\d+)\) (.+?)(?=^\d+\)|$)'
ref_entries = {}

for match in re.finditer(ref_pattern, refs_content, re.MULTILINE | re.DOTALL):
    old_num = int(match.group(1))
    ref_text = match.group(2).strip()
    ref_entries[old_num] = ref_text

print(f"\n抽出した文献数: {len(ref_entries)}")

# 新しい順序で並べ替え（40番を除外）
sorted_refs = []
for old_num in sorted(old_to_new.keys()):
    new_num = old_to_new[old_num]
    if old_num in ref_entries:
        sorted_refs.append((new_num, ref_entries[old_num]))
    else:
        print(f"⚠️ 警告: {old_num}番の文献が見つかりません")

# 新しいReferencesセクションを生成
new_refs_content = "# References\n\n"
for new_num, ref_text in sorted(sorted_refs):
    new_refs_content += f"{new_num}) {ref_text}\n\n"

new_refs_content += "---\n\n"  # セクション区切り

print(f"✓ Referencesセクションを{len(sorted_refs)}個の文献で再構築しました")

# 40番（Shin et al.）を削除したことを記録
print("\n注意: 40) Shin et al. (Mental health) は削除されました（糖尿病との関連性が低いため）")

# 統合して保存
final_content = modified_content + new_refs_content

# Tablesセクションを追加（元のファイルから）
tables_start = content.find("# Tables and Figures")
if tables_start != -1:
    tables_content = content[tables_start:]
    final_content += tables_content

# 最終版を保存
output_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes_final.qmd"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"\n✓ 最終版を保存: {output_path}")

# 検証: 引用番号が1-39の連番になっているか確認
citation_pattern = r'(?<=[a-zA-Z\s\.])\d+\)(?:,\s*\d+\))*'
found_citations = set()

for line in modified_content.split('\n'):
    # 統計値を含む行をスキップ
    if any(pattern in line for pattern in ['(N = ', 'p = ', 'β = ', '| ', 'Min', 'Max']):
        continue

    for match in re.finditer(citation_pattern, line):
        citation_text = match.group()
        before_char = line[match.start() - 1] if match.start() > 0 else ' '
        if before_char.isdigit() or before_char in '.,':
            continue

        numbers = re.findall(r'\d+', citation_text)
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 50:
                found_citations.add(num)

print("\n" + "=" * 80)
print("検証結果")
print("=" * 80)

expected_citations = set(range(1, 40))  # 1-39
missing = sorted(expected_citations - found_citations)
extra = sorted(found_citations - expected_citations)

if missing:
    print(f"\n⚠️ 引用されていない番号: {missing}")
else:
    print("\n✓ 全ての文献（1-39）が引用されています")

if extra:
    print(f"\n⚠️ 予期しない番号が検出されました: {extra}")
    print("（これらは統計値の可能性があります）")

print("\n" + "=" * 80)
print("完了！")
print("=" * 80)
print("\n次のステップ:")
print("1. Manuscript_PM25_diabetes_final.qmd を確認")
print("2. 引用内容の科学的整合性を確認")
print("3. 元のファイルと置き換え")
