"""
本文中の引用番号を正確に抽出するスクリプト（改善版）
統計値を除外し、文献引用のみを抽出する
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Referencesセクション開始行を特定
refs_line_num = None
for i, line in enumerate(lines):
    if line.strip() == "# References":
        refs_line_num = i
        break

if refs_line_num is None:
    refs_line_num = len(lines)

# 本文部分のみ
main_lines = lines[:refs_line_num]

# 引用番号を抽出（改善版パターン）
# 文の途中や末尾に出現する "数字)" または "数字),数字)" の形式のみ
citation_pattern = r'(?<=[a-zA-Z\s\.])\d+\)(?:,\s*\d+\))*'

cited_numbers = set()
first_appearance = {}
current_pos = 0

for line_num, line in enumerate(main_lines):
    # 統計値を含む行をスキップ
    if any(pattern in line for pattern in [
        '(N = ', '(n = ', 'p = 0.', 'β = ', 'SE = ',
        'CI = ', 'R² = ', 'HR = ', 'OR = ', 'AIC', 'BIC',
        'Min', 'Max', 'Mean', 'SD', 'Median',
        '| ', '|---',  # テーブル行
    ]):
        current_pos += len(line)
        continue

    # テーブル内の数値をスキップ
    if re.search(r'\|\s*\d+\.?\d*\s*\|', line):
        current_pos += len(line)
        continue

    # 引用パターンを検索
    for match in re.finditer(citation_pattern, line):
        citation_text = match.group()

        # 前後のコンテキストを確認（より厳密に）
        start_in_line = max(0, match.start() - 30)
        end_in_line = min(len(line), match.end() + 30)
        context = line[start_in_line:end_in_line]

        # 除外パターン
        if any(pattern in context for pattern in [
            '=', '±', '>', '<', '(', '10,000', 'μg/m³',
            'per 100,000', 'year', 'age'
        ]):
            continue

        # 数値の一部でないことを確認
        before_char = line[match.start() - 1] if match.start() > 0 else ' '
        if before_char.isdigit() or before_char in '.,':
            continue

        # 引用番号を抽出
        numbers = re.findall(r'\d+', citation_text)
        for num_str in numbers:
            num = int(num_str)
            # 妥当な範囲のみ（1-50）
            if 1 <= num <= 50:
                cited_numbers.add(num)
                if num not in first_appearance:
                    first_appearance[num] = (line_num + 1, current_pos + match.start())
                    print(f"Line {line_num + 1}: 引用 {num}) 検出 - {line.strip()[:60]}...")

    current_pos += len(line)

# 1-40の全番号
all_numbers = set(range(1, 41))

# 未引用番号
uncited_numbers = sorted(all_numbers - cited_numbers)

print("\n" + "=" * 80)
print("引用状況の分析結果")
print("=" * 80)

print(f"\n✓ 引用されている番号 (合計 {len(cited_numbers)} 個):")
cited_sorted = sorted(cited_numbers)
print(cited_sorted)

print(f"\n✗ 引用されていない番号 (合計 {len(uncited_numbers)} 個):")
print(uncited_numbers)

# 未引用文献の内容を表示
if uncited_numbers:
    print("\n" + "=" * 80)
    print("未引用文献の詳細")
    print("=" * 80)

    # Referencesセクションを解析
    refs_lines = lines[refs_line_num:]
    refs_content = ''.join(refs_lines)

    for num in uncited_numbers:
        # 該当番号の文献を抽出
        pattern = rf'^{num}\) (.+?)(?=^\d+\)|$)'
        match = re.search(pattern, refs_content, re.MULTILINE | re.DOTALL)
        if match:
            ref_text = match.group(1).strip()
            # 改行を削除
            ref_text = ' '.join(ref_text.split())
            # 最初の150文字のみ表示
            ref_short = ref_text[:150] + "..." if len(ref_text) > 150 else ref_text
            print(f"\n{num}) {ref_short}")

# 初登場順の確認
print("\n" + "=" * 80)
print("初登場順の確認")
print("=" * 80)

# 初登場順に並べる
sorted_by_appearance = sorted(first_appearance.items(), key=lambda x: x[1])

print("\n初登場順（現在の番号）:")
appearance_order = [num for num, _ in sorted_by_appearance]
print(appearance_order)

# 番号と初登場順が一致しているかチェック
expected_order = list(range(1, len(sorted_by_appearance) + 1))
if appearance_order == expected_order:
    print("\n✓ 初登場順は正しく並んでいます")
else:
    print("\n✗ 初登場順が正しくありません")
    print(f"\n現在の初登場順: {appearance_order[:10]}...")
    print(f"正しい初登場順: {expected_order[:10]}...")

    # マッピング表を作成
    print("\n引用番号の再割り当てが必要です：")
    print("現在番号 → 新番号")
    for i, current_num in enumerate(appearance_order[:20], 1):
        if current_num != i:
            print(f"  {current_num} → {i}")

print("\n" + "=" * 80)
