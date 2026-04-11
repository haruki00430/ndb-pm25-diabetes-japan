"""
文献2), 3)を削除し、以降の番号を繰り上げるスクリプト

削除する文献：
- 2) Brook et al. 2010 - Cardiovascular disease
- 3) Rajagopalan et al. 2018 - Cardiovascular disease

番号の変更：
- 1 → 1 (変更なし)
- 2 → 削除
- 3 → 削除
- 4 → 2
- 5 → 3
- 6 → 4
- ...
- 39 → 37
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# バックアップ作成
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
backup_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd.backup_remove_2_3"

print("=" * 100)
print("文献2), 3)の削除と番号繰り上げ")
print("=" * 100)

# バックアップ
import shutil
shutil.copy(manuscript_path, backup_path)
print(f"\n✓ バックアップを作成: {backup_path.name}")

# 原稿を読み込み
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Referencesセクションを分離
refs_start = content.find("# References")
main_content = content[:refs_start]
refs_section = content[refs_start:]

# ===== Step 1: マッピングテーブルを作成 =====
print("\n[Step 1] 番号マッピングテーブルを作成")
print("-" * 100)

# 旧番号 → 新番号のマッピング
old_to_new = {}
old_to_new[1] = 1  # 1番は変更なし
# 2番と3番は削除（マッピングなし）
for old_num in range(4, 40):  # 4-39
    new_num = old_num - 2  # 2つ繰り上げ
    old_to_new[old_num] = new_num

print(f"マッピング数: {len(old_to_new)} 件")
print("最初の10件:")
for old_num in range(1, 11):
    if old_num in old_to_new:
        print(f"  {old_num} → {old_to_new[old_num]}")
    else:
        print(f"  {old_num} → 削除")

# ===== Step 2: 本文中の引用番号をプレースホルダに変換 =====
print("\n[Step 2] 本文中の引用番号をプレースホルダに変換")
print("-" * 100)

# 引用パターン（単独または連続）
# 重要：降順で置換（大きい番号から順に）して、既に置換した番号との混同を避ける
modified_content = main_content

# 統計値を含むパターン（置換対象外）
exclude_patterns = [
    r'\(N\s*=\s*\d+\)',
    r'\(n\s*=\s*\d+\)',
    r'p\s*=\s*0\.\d+',
    r'β\s*=\s*',
    r'HR\s*=\s*\d+\.\d+',
    r'CI\s*=\s*\d+\.\d+',
    r'95%\s*CI\s*=\s*\d+\.\d+',
]

conversion_count = 0

# 降順で置換（39番から1番へ）
for old_num in sorted(old_to_new.keys(), reverse=True):
    new_num = old_to_new[old_num]

    # パターン：引用番号の形式は "XX)" または "XX)," または "XX). "
    # 前の文字が数字や等号でないことを確認
    pattern = rf'(?<=[a-zA-Z\s\.\)\]])({old_num}\))'

    # プレースホルダに変換
    placeholder = f"##REF_{old_num}##"

    # 置換前の出現回数をカウント
    matches = list(re.finditer(pattern, modified_content))

    if matches:
        # 統計値を含む行を除外
        valid_matches = []
        for match in matches:
            # マッチ箇所の前後100文字を取得
            start = max(0, match.start() - 100)
            end = min(len(modified_content), match.end() + 100)
            context = modified_content[start:end]

            # 統計値パターンが含まれていないかチェック
            is_statistical = any(re.search(pat, context) for pat in exclude_patterns)

            if not is_statistical:
                valid_matches.append(match)

        if valid_matches:
            # 置換実行（後ろから順に）
            for match in reversed(valid_matches):
                modified_content = (
                    modified_content[:match.start(1)] +
                    placeholder +
                    modified_content[match.end(1):]
                )
                conversion_count += 1

print(f"✓ {conversion_count} 箇所をプレースホルダに変換しました")

# 2番と3番が残っていないか確認
remaining_2_3 = []
for line in modified_content.split('\n'):
    if re.search(r'(?<=[a-zA-Z\s\.\)\]])[23]\)', line):
        # 統計値でないか確認
        is_statistical = any(re.search(pat, line) for pat in exclude_patterns)
        if not is_statistical:
            remaining_2_3.append(line.strip()[:100])

if remaining_2_3:
    print(f"\n⚠️ 警告: 2)または3)が残っている可能性があります（最初の3件）:")
    for line in remaining_2_3[:3]:
        print(f"  {line}...")

# ===== Step 3: プレースホルダを新番号に置換 =====
print("\n[Step 3] プレースホルダを新番号に置換")
print("-" * 100)

replacement_count = 0

for old_num in sorted(old_to_new.keys(), reverse=True):
    new_num = old_to_new[old_num]
    placeholder = f"##REF_{old_num}##"
    new_citation = f"{new_num})"

    count = modified_content.count(placeholder)
    if count > 0:
        modified_content = modified_content.replace(placeholder, new_citation)
        replacement_count += count
        if old_num != new_num:
            print(f"  ##REF_{old_num}## → {new_num}) ({count} 箇所)")

print(f"\n✓ {replacement_count} 箇所を新番号に置換しました")

# ===== Step 4: Referencesセクションから2番と3番を削除 =====
print("\n[Step 4] References セクションから2番と3番を削除")
print("-" * 100)

# 文献エントリを抽出
ref_pattern = r'^(\d+)\) (.+?)(?=^\d+\)|$)'
ref_entries = {}

for match in re.finditer(ref_pattern, refs_section, re.MULTILINE | re.DOTALL):
    old_num = int(match.group(1))
    ref_text = match.group(2).strip()
    ref_entries[old_num] = ref_text

print(f"抽出した文献数: {len(ref_entries)}")

# 削除する文献を表示
if 2 in ref_entries:
    print(f"\n削除: 2) {ref_entries[2][:100]}...")
if 3 in ref_entries:
    print(f"削除: 3) {ref_entries[3][:100]}...")

# ===== Step 5: Referencesセクションを再構築 =====
print("\n[Step 5] References セクションを再構築")
print("-" * 100)

new_refs_content = "# References\n\n"

# 新しい順序で並べる（2と3を除外）
sorted_refs = []
for old_num in sorted(old_to_new.keys()):
    new_num = old_to_new[old_num]
    if old_num in ref_entries:
        sorted_refs.append((new_num, ref_entries[old_num]))

for new_num, ref_text in sorted_refs:
    new_refs_content += f"{new_num}) {ref_text}\n\n"

new_refs_content += "---\n\n"

print(f"✓ References セクションを {len(sorted_refs)} 個の文献で再構築しました（37個）")

# ===== Step 6: 統合して保存 =====
final_content = modified_content + new_refs_content

# Tablesセクションを追加（元のファイルから）
tables_start = content.find("# Tables and Figures")
if tables_start != -1:
    tables_content = content[tables_start:]
    final_content += tables_content

# 保存
with open(manuscript_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"\n✓ 更新版を保存: {manuscript_path.name}")

# ===== Step 7: 検証 =====
print("\n[Step 7] 検証")
print("-" * 100)

# 引用番号が1-37の連番になっているか確認
citation_pattern = r'(?<=[a-zA-Z\s\.\)\]])(\d+)\)(?:,\s*(\d+)\))*'
found_citations = set()

for line in modified_content.split('\n'):
    # 統計値を含む行をスキップ
    if any(re.search(pat, line) for pat in exclude_patterns):
        continue

    # Table行をスキップ
    if '|' in line:
        continue

    for match in re.finditer(citation_pattern, line):
        citation_text = match.group()
        numbers = re.findall(r'\d+', citation_text)
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 50:
                found_citations.add(num)

expected_citations = set(range(1, 38))  # 1-37
missing = sorted(expected_citations - found_citations)
extra = sorted(found_citations - expected_citations)

if missing:
    print(f"\n⚠️ 引用されていない番号: {missing}")
else:
    print("\n✓ 全ての文献（1-37）が引用されています")

if extra:
    print(f"\n⚠️ 予期しない番号が検出されました: {extra}")
    print("（これらは統計値の可能性があります）")

print("\n" + "=" * 100)
print("完了！")
print("=" * 100)
print("\n次のステップ:")
print("1. Manuscript_PM25_diabetes.qmd を確認")
print("2. 引用1),4),5) が Introduction に正しく表示されているか確認")
print("3. References セクションが2番と3番なしで再構築されているか確認")
print(f"4. 問題があれば、バックアップ {backup_path.name} から復元")
