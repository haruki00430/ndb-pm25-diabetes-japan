"""
本文中の引用番号を抽出し、未引用文献を特定するスクリプト
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Referencesセクションより前の本文部分のみを対象
refs_start = content.find("# References")
if refs_start == -1:
    refs_start = len(content)
main_content = content[:refs_start]

# 引用番号のパターンを抽出（文脈を考慮）
# 統計値 (N = 47), (p = 0.047) などを除外
citation_pattern = r'(?<![=\s])\d+\)(?:,\d+\))*'

# 全ての引用箇所を取得
all_matches = []
for match in re.finditer(citation_pattern, main_content):
    # 前後のコンテキストを確認
    start = max(0, match.start() - 20)
    end = min(len(main_content), match.end() + 20)
    context = main_content[start:end]

    # 統計値パターンを除外
    exclude_patterns = [
        r'\(N\s*=\s*\d+\)',
        r'\(n\s*=\s*\d+\)',
        r'p\s*=\s*0\.\d+',
        r'HR\s*=\s*\d+',
        r'OR\s*=\s*\d+',
        r'β\s*=',
        r'CI\s*=',
        r'R²\s*=',
    ]

    is_stat = False
    for pattern in exclude_patterns:
        if re.search(pattern, context):
            is_stat = True
            break

    if not is_stat:
        all_matches.append((match.group(), match.start()))

# 引用番号を抽出
cited_numbers = set()
for citation_text, pos in all_matches:
    # "1),2),3)" のような複数引用を分解
    numbers = re.findall(r'\d+', citation_text)
    cited_numbers.update(int(n) for n in numbers)

# 1-40の全番号
all_numbers = set(range(1, 41))

# 未引用番号
uncited_numbers = sorted(all_numbers - cited_numbers)

print("=" * 80)
print("引用状況の分析結果")
print("=" * 80)

print(f"\n✓ 引用されている番号 (合計 {len(cited_numbers)} 個):")
print(sorted(cited_numbers))

print(f"\n✗ 引用されていない番号 (合計 {len(uncited_numbers)} 個):")
print(uncited_numbers)

# 未引用文献の内容を表示
if uncited_numbers:
    print("\n" + "=" * 80)
    print("未引用文献の詳細")
    print("=" * 80)

    # Referencesセクションを解析
    refs_section = content[refs_start:]
    for num in uncited_numbers:
        # 該当番号の文献を抽出
        pattern = rf'^{num}\) (.+?)(?=^\d+\)|$)'
        match = re.search(pattern, refs_section, re.MULTILINE | re.DOTALL)
        if match:
            ref_text = match.group(1).strip()
            # 最初の100文字のみ表示
            ref_short = ref_text[:100] + "..." if len(ref_text) > 100 else ref_text
            print(f"\n{num}) {ref_short}")

# 初登場順の確認
print("\n" + "=" * 80)
print("初登場順の確認")
print("=" * 80)

first_appearance = {}
for citation_text, pos in sorted(all_matches, key=lambda x: x[1]):
    numbers = re.findall(r'\d+', citation_text)
    for num_str in numbers:
        num = int(num_str)
        if num not in first_appearance:
            first_appearance[num] = pos

# 初登場順に並べる
sorted_by_appearance = sorted(first_appearance.items(), key=lambda x: x[1])

print("\n初登場順（現在の番号）:")
appearance_order = [num for num, _ in sorted_by_appearance]
print(appearance_order)

# 番号と初登場順が一致しているかチェック
correct_order = list(range(1, len(sorted_by_appearance) + 1))
if appearance_order == correct_order:
    print("\n✓ 初登場順は正しく並んでいます")
else:
    print("\n✗ 初登場順が正しくありません")
    print("\n修正が必要な番号:")
    for i, (actual, expected) in enumerate(zip(appearance_order, correct_order), 1):
        if actual != expected:
            print(f"  位置 {i}: 現在 {actual} → 正しくは {expected} であるべき")

print("\n" + "=" * 80)
