"""
全36文献の実在性と整合性を確認するスクリプト
1. 各文献の基本情報を抽出
2. 本文中での引用箇所を抽出
3. 文脈との整合性をチェック
4. 実在性の簡易チェック
"""
import re
from pathlib import Path
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 100)
print("全36文献の実在性と整合性チェック")
print("=" * 100)

# Referencesセクションを分離
refs_start = content.find("# References")
main_content = content[:refs_start]
refs_section = content[refs_start:]

# ===== Step 1: References セクションから全文献を抽出 =====
print("\n[Step 1] References セクションから全36文献を抽出\n")

# 各行を読み取り
ref_entries = {}
current_num = None
current_lines = []

for line in refs_section.split('\n'):
    # 番号で始まる行を検出
    match = re.match(r'^(\d+)\)\s+(.+)', line)
    if match:
        # 前の文献を保存
        if current_num is not None and current_lines:
            full_text = ' '.join(current_lines)
            ref_entries[current_num] = full_text
        # 新しい文献を開始
        current_num = int(match.group(1))
        current_lines = [match.group(2)]
    elif current_num is not None and line.strip() and not line.startswith('#') and not line.startswith('-'):
        # 前の文献の続き
        current_lines.append(line.strip())

# 最後の文献を保存
if current_num is not None and current_lines:
    full_text = ' '.join(current_lines)
    ref_entries[current_num] = full_text

print(f"✓ 抽出した文献数: {len(ref_entries)}")

# 各文献の詳細を解析
references = {}
for num, full_text in ref_entries.items():
    # 著者を抽出（最初のピリオドまたはカンマまで）
    author_match = re.match(r'^([^\.]+?)(?:\.|\s+\()', full_text)
    authors = author_match.group(1).strip() if author_match else "Unknown"

    # 年を抽出
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', full_text)
    year = year_match.group(1) if year_match else "Unknown"

    # DOIを抽出
    doi_match = re.search(r'doi:(10\.\S+)', full_text)
    doi = doi_match.group(1) if doi_match else None

    # タイトルとジャーナルを推定（簡易版）
    # ピリオドで区切って2番目と3番目がタイトルとジャーナル
    parts = full_text.split('.')
    title = parts[1].strip() if len(parts) > 1 else "Unknown"
    journal = parts[2].strip() if len(parts) > 2 else "Unknown"

    references[num] = {
        'authors': authors,
        'title': title,
        'journal': journal,
        'year': year,
        'doi': doi,
        'full_text': full_text
    }

# ===== Step 2: 本文中の引用箇所を抽出 =====
print("\n[Step 2] 本文中の引用箇所を抽出\n")

# 引用パターン
citation_pattern = r'(?<=[a-zA-Z\s\.\)\]])(\d+)\)(?:,\s*(\d+)\))*'

# 統計値除外パターン
exclude_patterns = [
    r'\(N\s*=\s*\d+\)',
    r'\(n\s*=\s*\d+\)',
    r'p\s*=\s*0\.\d+',
    r'β\s*=\s*',
    r'HR\s*=\s*\d+\.\d+',
    r'CI\s*=\s*\d+\.\d+',
]

citation_locations = defaultdict(list)

lines = main_content.split('\n')
for line_num, line in enumerate(lines, 1):
    # 統計値を含む行をスキップ
    if any(re.search(pattern, line) for pattern in exclude_patterns):
        continue
    # Tableをスキップ
    if '|' in line:
        continue

    # 引用を検出
    for match in re.finditer(citation_pattern, line):
        citation_text = match.group()
        numbers = re.findall(r'\d+', citation_text)

        # 文脈を抽出
        start_pos = max(0, match.start() - 60)
        end_pos = min(len(line), match.end() + 60)
        context = line[start_pos:end_pos].strip()

        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 36:
                citation_locations[num].append({
                    'line_num': line_num,
                    'context': context
                })

print(f"✓ {sum(len(v) for v in citation_locations.values())} 箇所の引用を検出")
print(f"✓ {len(citation_locations)} 個の文献が引用されています")

# 未引用文献
cited_refs = set(citation_locations.keys())
all_refs = set(range(1, 37))
uncited_refs = sorted(all_refs - cited_refs)

if uncited_refs:
    print(f"\n⚠️ 未引用の文献: {uncited_refs}")
else:
    print("\n✓ 全36文献が引用されています")

# ===== Step 3: 各文献の詳細チェック =====
print("\n" + "=" * 100)
print("[Step 3] 各文献の詳細チェック")
print("=" * 100)

# 主要な文献（1-12番）を詳しくチェック
important_nums = list(range(1, 13))

issues = []

for num in important_nums:
    if num not in references:
        continue

    ref = references[num]
    print(f"\n{'─' * 100}")
    print(f"[{num}] {ref['authors']} ({ref['year']})")
    print(f"タイトル: {ref['title'][:100]}...")
    print(f"ジャーナル: {ref['journal'][:60]}...")
    print(f"DOI: {ref['doi'] if ref['doi'] else '❌ なし'}")

    # 引用箇所
    if num in citation_locations:
        locs = citation_locations[num]
        print(f"引用箇所: {len(locs)} 箇所")
        for i, loc in enumerate(locs[:2], 1):  # 最初の2箇所のみ表示
            print(f"  [{i}] (行 {loc['line_num']}): ...{loc['context'][:80]}...")
    else:
        print("引用箇所: ❌ 未引用")
        issues.append({'num': num, 'issue': '未引用'})

    # チェック項目
    checks = []

    # 1. 年の妥当性
    year_int = int(ref['year']) if ref['year'].isdigit() else 0
    if year_int < 1990 or year_int > 2026:
        checks.append(f"⚠️ 年が範囲外: {ref['year']}")

    # 2. DOIの有無と形式
    if ref['doi']:
        if not ref['doi'].startswith('10.'):
            checks.append(f"⚠️ DOI形式が不正: {ref['doi']}")
    else:
        # 政府機関データはDOIなしでもOK
        if 'National Institute' not in ref['authors'] and 'Ministry of' not in ref['authors']:
            checks.append("⚠️ DOI がありません")

    # 3. タイトルのキーワードチェック
    title_lower = ref['title'].lower()
    has_diabetes = 'diabetes' in title_lower or 'diabetic' in title_lower or 'glucose' in title_lower
    has_pm25 = 'pm2.5' in title_lower or 'particulate' in title_lower or 'air pollution' in title_lower
    has_metabolic = 'metabolic' in title_lower or 'insulin' in title_lower

    if num <= 6:  # メタアナリシス・レビュー
        if not (has_diabetes or has_metabolic):
            checks.append("⚠️ タイトルに diabetes/metabolic が含まれていません")

    # チェック結果
    if checks:
        for check in checks:
            print(f"  {check}")
        issues.append({'num': num, 'issue': ', '.join(checks)})
    else:
        print("  ✓ 基本的なチェックに問題なし")

# ===== Step 4: 残りの文献（13-36番）の簡易チェック =====
print("\n" + "=" * 100)
print("[Step 4] 残りの文献（13-36番）の簡易チェック")
print("=" * 100)

other_nums = list(range(13, 37))
other_issues = []

for num in other_nums:
    if num not in references:
        continue

    ref = references[num]

    # 簡易チェック
    checks = []

    # 年の妥当性
    year_int = int(ref['year']) if ref['year'].isdigit() else 0
    if year_int < 1990 or year_int > 2026:
        checks.append(f"年が範囲外: {ref['year']}")

    # DOI
    if not ref['doi']:
        if 'National Institute' not in ref['authors'] and 'Ministry of' not in ref['authors']:
            checks.append("DOI なし")

    # 未引用
    if num not in citation_locations:
        checks.append("未引用")

    if checks:
        other_issues.append({'num': num, 'authors': ref['authors'][:40], 'checks': checks})

if other_issues:
    print(f"\n⚠️ 要確認の文献: {len(other_issues)} 件\n")
    for issue in other_issues:
        print(f"[{issue['num']}] {issue['authors']}...")
        for check in issue['checks']:
            print(f"  - {check}")
else:
    print("\n✓ 全ての文献（13-36番）が基本的なチェックをパスしました")

# ===== Step 5: サマリー =====
print("\n" + "=" * 100)
print("サマリー")
print("=" * 100)

print(f"\n総文献数: {len(references)}")
print(f"引用されている文献: {len(cited_refs)}/{len(all_refs)} ({len(cited_refs)/len(all_refs)*100:.1f}%)")

if uncited_refs:
    print(f"\n⚠️ 未引用の文献: {uncited_refs}")

if issues:
    print(f"\n⚠️ 主要文献（1-12番）の要確認: {len(issues)} 件")

if other_issues:
    print(f"⚠️ その他の文献（13-36番）の要確認: {len(other_issues)} 件")

print("\n" + "=" * 100)
print("推奨される次のステップ")
print("=" * 100)
print("""
1. 未引用の文献について、本文中で引用すべき箇所を特定
2. 要確認の文献について、PubMed/Google Scholarで実在を確認
3. 特に重要な文献（1-6番：メタアナリシス）について原文を確認
4. DOIがない文献について、正しいDOIを追加

特に確認すべき文献：
- メタアナリシス（1, 4, 5, 11番）: これらは主要結果の根拠となる重要文献
- 政府データ（7, 8番）: アクセス日を確認
- 日本の研究（9, 22, 23, 24番）: 本文での引用箇所が適切か確認
""")
