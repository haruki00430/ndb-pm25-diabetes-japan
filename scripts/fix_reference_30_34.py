"""
30番を削除し、34番を145行目に追加するスクリプト

作業内容：
1. 145行目: 33),35) → 33),34),35)
2. References から30番を削除
3. 31-36番を30-35番に繰り上げ
"""
import re
from pathlib import Path
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

# バックアップ作成
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
backup_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd.backup_fix_30_34"

print("=" * 100)
print("30番削除と34番追加")
print("=" * 100)

# バックアップ
shutil.copy(manuscript_path, backup_path)
print(f"\n✓ バックアップを作成: {backup_path.name}")

# 原稿を読み込み
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Referencesセクションを分離
refs_start = content.find("# References")
main_content = content[:refs_start]
refs_section = content[refs_start:]

# ===== Step 1: 145行目の修正 =====
print("\n[Step 1] 145行目に34番を追加")
print("-" * 100)

old_text_145 = "Similar administrative data approaches have been successfully used in Japanese PM2.5 health research 33),35)."
new_text_145 = "Similar administrative data approaches have been successfully used in Japanese PM2.5 health research 33),34),35)."

if old_text_145 in main_content:
    main_content = main_content.replace(old_text_145, new_text_145)
    print("✓ 145行目を修正: 33),35) → 33),34),35)")
else:
    print("⚠️ 警告: 145行目の該当箇所が見つかりませんでした")

# ===== Step 2: 本文中の引用番号をプレースホルダに変換 =====
print("\n[Step 2] 本文中の引用番号をプレースホルダに変換（31-36番のみ）")
print("-" * 100)

# 統計値除外パターン
exclude_patterns = [
    r'\(N\s*=\s*\d+\)',
    r'\(n\s*=\s*\d+\)',
    r'p\s*=\s*0\.\d+',
    r'β\s*=\s*',
    r'HR\s*=\s*\d+\.\d+',
    r'CI\s*=\s*\d+\.\d+',
]

modified_content = main_content
conversion_count = 0

# 降順で置換（36番から31番へ、1-30番は変更なし）
for old_num in range(36, 30, -1):  # 36, 35, 34, 33, 32, 31
    new_num = old_num - 1  # 1つ繰り上げ

    # パターン
    pattern = rf'(?<=[a-zA-Z\s\.\)\]])({old_num}\))'

    # プレースホルダに変換
    placeholder = f"##REF_{old_num}##"

    # 置換前の出現回数をカウント
    matches = list(re.finditer(pattern, modified_content))

    if matches:
        valid_matches = []
        for match in matches:
            start = max(0, match.start() - 100)
            end = min(len(modified_content), match.end() + 100)
            context = modified_content[start:end]

            is_statistical = any(re.search(pat, context) for pat in exclude_patterns)

            if not is_statistical:
                valid_matches.append(match)

        if valid_matches:
            for match in reversed(valid_matches):
                modified_content = (
                    modified_content[:match.start(1)] +
                    placeholder +
                    modified_content[match.end(1):]
                )
                conversion_count += 1

print(f"✓ {conversion_count} 箇所をプレースホルダに変換しました")

# ===== Step 3: プレースホルダを新番号に置換 =====
print("\n[Step 3] プレースホルダを新番号に置換")
print("-" * 100)

replacement_count = 0

for old_num in range(36, 30, -1):
    new_num = old_num - 1
    placeholder = f"##REF_{old_num}##"
    new_citation = f"{new_num})"

    count = modified_content.count(placeholder)
    if count > 0:
        modified_content = modified_content.replace(placeholder, new_citation)
        replacement_count += count
        print(f"  ##REF_{old_num}## → {new_num}) ({count} 箇所)")

print(f"\n✓ {replacement_count} 箇所を新番号に置換しました")

# ===== Step 4: Referencesセクションを再構築 =====
print("\n[Step 4] References セクションを再構築（30番を削除）")
print("-" * 100)

# References セクションの各行を読み取り
ref_entries = {}
current_num = None
current_lines = []

for line in refs_section.split('\n'):
    match = re.match(r'^(\d+)\)\s+(.+)', line)
    if match:
        # 前の文献を保存
        if current_num is not None and current_lines:
            ref_entries[current_num] = '\n'.join(current_lines)
        # 新しい文献を開始
        current_num = int(match.group(1))
        current_lines = [match.group(2)]
    elif current_num is not None and line.strip() and not line.startswith('#') and not line.startswith('-'):
        current_lines.append(line.strip())

# 最後の文献を保存
if current_num is not None and current_lines:
    ref_entries[current_num] = '\n'.join(current_lines)

print(f"抽出した文献数: {len(ref_entries)}")

# 30番を削除
if 30 in ref_entries:
    deleted_ref = ref_entries[30]
    print(f"\n削除: 30) {deleted_ref[:80]}...")
    del ref_entries[30]

# 新しいReferencesセクションを生成
new_refs_content = "# References\n\n"

# 1-29番はそのまま、31-36番を30-35番に
for old_num in sorted(ref_entries.keys()):
    if old_num <= 29:
        new_num = old_num
    elif old_num >= 31:
        new_num = old_num - 1
    else:
        continue  # 30番はスキップ

    ref_text = ref_entries[old_num]
    new_refs_content += f"{new_num}) {ref_text}\n\n"

new_refs_content += "---\n\n"

print(f"✓ References セクションを {len(ref_entries) - 1} 個の文献で再構築しました（35個）")

# ===== Step 5: 統合して保存 =====
final_content = modified_content + new_refs_content

# Tablesセクションを追加
tables_start = content.find("# Tables and Figures")
if tables_start != -1:
    tables_content = content[tables_start:]
    final_content += tables_content

# 保存
with open(manuscript_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"\n✓ 更新版を保存: {manuscript_path.name}")

# ===== Step 6: 検証 =====
print("\n[Step 6] 検証")
print("-" * 100)

# 引用番号が1-35の連番になっているか確認
citation_pattern = r'(?<=[a-zA-Z\s\.\)\]])(\d+)\)(?:,\s*(\d+)\))*'
found_citations = set()

for line in modified_content.split('\n'):
    if any(re.search(pat, line) for pat in exclude_patterns):
        continue
    if '|' in line:
        continue

    for match in re.finditer(citation_pattern, line):
        citation_text = match.group()
        numbers = re.findall(r'\d+', citation_text)
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 40:
                found_citations.add(num)

expected_citations = set(range(1, 36))  # 1-35
missing = sorted(expected_citations - found_citations)
extra = sorted(found_citations - expected_citations)

if missing:
    print(f"\n⚠️ 引用されていない番号: {missing}")
else:
    print("\n✓ 全ての文献（1-35）が引用されています")

if extra:
    print(f"\n⚠️ 予期しない番号: {extra}")
    print("（これらは統計値の可能性があります）")

# 145行目の確認
if "33),34),35)" in modified_content:
    print("\n✓ 145行目に34番が追加されました")
else:
    print("\n⚠️ 警告: 145行目の修正を確認できませんでした")

print("\n" + "=" * 100)
print("完了！")
print("=" * 100)
print("\n次のステップ:")
print("1. Manuscript_PM25_diabetes.qmd を確認")
print("2. 145行目に 33),34),35) が表示されているか確認")
print("3. References セクションが1-35番の連番になっているか確認")
print(f"4. 問題があれば、バックアップ {backup_path.name} から復元")
