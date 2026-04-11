"""
7番欠番を解消するスクリプト
8-37番を7-36番に繰り上げる

番号の変更：
- 1-6 → 1-6 (変更なし)
- 7 → 欠番（削除済み）
- 8 → 7
- 9 → 8
- ...
- 37 → 36
"""
import re
from pathlib import Path
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

# バックアップ作成
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
backup_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd.backup_fix_gap7"

print("=" * 100)
print("7番欠番の解消（8-37番を7-36番に繰り上げ）")
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

# ===== Step 1: マッピングテーブルを作成 =====
print("\n[Step 1] 番号マッピングテーブルを作成")
print("-" * 100)

# 旧番号 → 新番号のマッピング
old_to_new = {}
# 1-6番は変更なし
for num in range(1, 7):
    old_to_new[num] = num
# 8-37番を7-36番に繰り上げ（1つずつ）
for old_num in range(8, 38):
    new_num = old_num - 1
    old_to_new[old_num] = new_num

print(f"マッピング数: {len(old_to_new)} 件")
print("変更される番号（最初の10件）:")
for old_num in range(8, 18):
    print(f"  {old_num} → {old_to_new[old_num]}")
print("  ...")

# ===== Step 2: 本文中の引用番号をプレースホルダに変換 =====
print("\n[Step 2] 本文中の引用番号をプレースホルダに変換")
print("-" * 100)

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

modified_content = main_content
conversion_count = 0

# 降順で置換（37番から8番へ、1-6番は変更なし）
for old_num in range(37, 7, -1):  # 37, 36, ..., 8
    new_num = old_to_new[old_num]

    # パターン：引用番号の形式は "XX)" または "XX)," または "XX). "
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

# ===== Step 3: プレースホルダを新番号に置換 =====
print("\n[Step 3] プレースホルダを新番号に置換")
print("-" * 100)

replacement_count = 0
changes = []

for old_num in range(37, 7, -1):  # 37, 36, ..., 8
    new_num = old_to_new[old_num]
    placeholder = f"##REF_{old_num}##"
    new_citation = f"{new_num})"

    count = modified_content.count(placeholder)
    if count > 0:
        modified_content = modified_content.replace(placeholder, new_citation)
        replacement_count += count
        if old_num != new_num:
            changes.append(f"  ##REF_{old_num}## → {new_num}) ({count} 箇所)")

# 最初の10件のみ表示
for change in changes[:10]:
    print(change)
if len(changes) > 10:
    print(f"  ... 他 {len(changes) - 10} 件")

print(f"\n✓ {replacement_count} 箇所を新番号に置換しました")

# ===== Step 4: Referencesセクションを再構築 =====
print("\n[Step 4] References セクションを再構築")
print("-" * 100)

# References セクションの各行を読み取り
ref_entries = {}
current_num = None
current_text = []

for line in refs_section.split('\n'):
    # 番号で始まる行を検出
    match = re.match(r'^(\d+)\)\s+(.+)', line)
    if match:
        # 前の文献を保存
        if current_num is not None:
            ref_entries[current_num] = '\n'.join(current_text)
        # 新しい文献を開始
        current_num = int(match.group(1))
        current_text = [match.group(2)]
    elif current_num is not None and line.strip():
        # 前の文献の続き
        current_text.append(line)
    elif not line.strip() and current_num is not None:
        # 空行で文献終了
        ref_entries[current_num] = '\n'.join(current_text)
        current_num = None
        current_text = []

# 最後の文献を保存
if current_num is not None:
    ref_entries[current_num] = '\n'.join(current_text)

print(f"抽出した文献数: {len(ref_entries)}")

# 新しいReferencesセクションを生成
new_refs_content = "# References\n\n"

# 新しい番号順に並べる
for old_num in sorted(old_to_new.keys()):
    new_num = old_to_new[old_num]
    if old_num in ref_entries:
        ref_text = ref_entries[old_num]
        new_refs_content += f"{new_num}) {ref_text}\n\n"

new_refs_content += "---\n\n"

print(f"✓ References セクションを {len(old_to_new)} 個の文献で再構築しました（36個）")

# ===== Step 5: 統合して保存 =====
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

# ===== Step 6: 検証 =====
print("\n[Step 6] 検証")
print("-" * 100)

# 引用番号が1-36の連番になっているか確認
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

expected_citations = set(range(1, 37))  # 1-36
missing = sorted(expected_citations - found_citations)
extra = sorted(found_citations - expected_citations)

if missing:
    print(f"\n⚠️ 引用されていない番号: {missing}")
else:
    print("\n✓ 全ての文献（1-36）が引用されています")

if extra:
    print(f"\n⚠️ 予期しない番号が検出されました: {extra}")
    print("（これらは統計値の可能性があります）")

print("\n" + "=" * 100)
print("完了！")
print("=" * 100)
print("\n次のステップ:")
print("1. Manuscript_PM25_diabetes.qmd を確認")
print("2. References セクションが1-36番の連番になっているか確認")
print("3. 全文献の実在性と内容の整合性を確認")
print(f"4. 問題があれば、バックアップ {backup_path.name} から復元")
