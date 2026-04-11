"""
全39文献の網羅的な整合性チェック
各引用箇所の文脈と、引用されている文献の内容が一致しているか確認する
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
print("全39文献の網羅的な整合性チェック")
print("=" * 100)

# Referencesセクションを分離
refs_start = content.find("# References")
main_content = content[:refs_start]
refs_section = content[refs_start:]

# ===== Step 1: References セクションから全文献情報を抽出 =====
print("\n[Step 1] References セクションから全39文献の情報を抽出中...\n")

ref_pattern = r'^(\d+)\) (.+?)\.(.+?)\.(.+?)\. (\d{4})'
references = {}

for match in re.finditer(ref_pattern, refs_section, re.MULTILINE):
    num = int(match.group(1))
    authors = match.group(2).strip()
    title = match.group(3).strip()
    journal = match.group(4).strip()
    year = match.group(5).strip()

    references[num] = {
        'authors': authors,
        'title': title,
        'journal': journal,
        'year': year
    }

print(f"✓ {len(references)} 個の文献を抽出しました")

# ===== Step 2: 本文から全引用箇所を抽出 =====
print("\n[Step 2] 本文から全引用箇所を抽出中...\n")

# 引用番号のパターン（単独または連続）
citation_pattern = r'(?<=[a-zA-Z\s\.\)])(\d+)\)(?:,\s*(\d+)\))*'

# 統計値を含む行を除外するパターン
exclude_patterns = [
    r'\(N\s*=\s*\d+\)',
    r'\(n\s*=\s*\d+\)',
    r'p\s*=\s*0\.\d+',
    r'β\s*=\s*',
    r'SE\s*=\s*',
    r'CI\s*=\s*',
    r'R²\s*=\s*',
    r'HR\s*=\s*',
    r'OR\s*=\s*',
    r'AIC\s*=\s*',
    r'BIC\s*=\s*',
    r'\|\s+',  # Table rows
    r'\|---',
    r'Min\s*=\s*',
    r'Max\s*=\s*',
    r'Mean\s*=\s*',
    r'SD\s*=\s*',
    r'Median\s*=\s*',
]

# 各引用番号の出現箇所を記録
citation_locations = defaultdict(list)

lines = main_content.split('\n')
for line_num, line in enumerate(lines, 1):
    # 統計値を含む行をスキップ
    if any(re.search(pattern, line) for pattern in exclude_patterns):
        continue

    # Tableヘッダー・区切り線をスキップ
    if '|' in line or line.strip().startswith('#'):
        continue

    # 引用を検出
    for match in re.finditer(citation_pattern, line):
        # マッチした引用番号を抽出
        citation_text = match.group()
        numbers = re.findall(r'\d+', citation_text)

        # 文脈を抽出（引用の前後50文字）
        start_pos = max(0, match.start() - 50)
        end_pos = min(len(line), match.end() + 50)
        context = line[start_pos:end_pos].strip()

        # 各番号を記録
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 39:
                citation_locations[num].append({
                    'line_num': line_num,
                    'context': context,
                    'full_line': line.strip()
                })

print(f"✓ {sum(len(v) for v in citation_locations.values())} 箇所の引用を検出しました")
print(f"✓ {len(citation_locations)} 個の文献が引用されています")

# ===== Step 3: 未引用文献を確認 =====
print("\n[Step 3] 未引用文献の確認\n")

cited_refs = set(citation_locations.keys())
all_refs = set(range(1, 40))
uncited_refs = sorted(all_refs - cited_refs)

if uncited_refs:
    print(f"⚠️ 未引用の文献が {len(uncited_refs)} 件あります:")
    for num in uncited_refs:
        if num in references:
            ref = references[num]
            print(f"  {num}) {ref['authors']} ({ref['year']}) - {ref['title'][:60]}...")
else:
    print("✓ 全39文献が引用されています")

# ===== Step 4: 各引用の整合性チェック =====
print("\n" + "=" * 100)
print("[Step 4] 各引用箇所の整合性チェック")
print("=" * 100)

# 主要なキーワード定義（文献の内容を推測するため）
keyword_definitions = {
    'diabetes': ['diabetes', 'diabetic', 'glycemic', 'glucose', 'HbA1c', 'insulin'],
    'PM2.5': ['PM2.5', 'particulate', 'air pollution', 'fine particle'],
    'meta-analysis': ['meta-analysis', 'systematic review', 'pooled'],
    'mechanism': ['mechanism', 'pathway', 'inflammation', 'oxidative stress', 'endothelial'],
    'Japan': ['Japan', 'Japanese', 'Tokyo', 'Okayama'],
    'China': ['China', 'Chinese'],
    'Europe': ['Europe', 'European', 'Germany', 'German', 'ESCAPE'],
    'North America': ['North America', 'United States', 'Canada', 'Ontario', 'Los Angeles'],
    'cohort': ['cohort', 'longitudinal', 'prospective'],
    'null': ['null', 'no association', 'non-significant', 'borderline'],
    'CKD': ['CKD', 'kidney', 'renal', 'ESRD'],
    'cardiovascular': ['cardiovascular', 'heart', 'CVD'],
}

# 各引用について整合性をチェック
issues = []
verified = 0

for ref_num in sorted(citation_locations.keys()):
    if ref_num not in references:
        continue

    ref = references[ref_num]
    locations = citation_locations[ref_num]

    print(f"\n{'─' * 100}")
    print(f"[文献 {ref_num}] {ref['authors']} ({ref['year']})")
    print(f"タイトル: {ref['title']}")
    print(f"引用箇所: {len(locations)} 箇所")

    # 文献タイトルから主要キーワードを抽出
    title_lower = ref['title'].lower()
    detected_keywords = []
    for category, keywords in keyword_definitions.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                detected_keywords.append(category)
                break

    print(f"文献の主要キーワード: {', '.join(set(detected_keywords)) if detected_keywords else '(未検出)'}")

    # 各引用箇所をチェック
    all_consistent = True
    for i, loc in enumerate(locations, 1):
        context_lower = loc['context'].lower()

        # 文脈から期待されるキーワードを推測
        context_keywords = []
        for category, keywords in keyword_definitions.items():
            for keyword in keywords:
                if keyword.lower() in context_lower:
                    context_keywords.append(category)
                    break

        # 整合性チェック：文献のキーワードと文脈のキーワードに重複があるか
        keyword_match = bool(set(detected_keywords) & set(context_keywords))

        status = "✓" if keyword_match or len(detected_keywords) == 0 else "⚠️"

        print(f"\n  引用箇所 {i}/{len(locations)} (行 {loc['line_num']}): {status}")
        print(f"    文脈: ...{loc['context']}...")
        print(f"    文脈キーワード: {', '.join(set(context_keywords)) if context_keywords else '(未検出)'}")

        if not keyword_match and len(detected_keywords) > 0:
            all_consistent = False
            issues.append({
                'ref_num': ref_num,
                'title': ref['title'],
                'context': loc['context'],
                'line_num': loc['line_num'],
                'ref_keywords': detected_keywords,
                'context_keywords': context_keywords,
            })
            print(f"    → ⚠️ 要確認: 文献のキーワードと文脈のキーワードが一致しません")

    if all_consistent:
        verified += 1

# ===== Step 5: 結果サマリー =====
print("\n" + "=" * 100)
print("整合性チェック結果サマリー")
print("=" * 100)

print(f"\n✓ 引用されている文献: {len(cited_refs)}/{len(all_refs)} ({len(cited_refs)/len(all_refs)*100:.1f}%)")
print(f"✓ 整合性を確認: {verified}/{len(cited_refs)} ({verified/len(cited_refs)*100:.1f}%)")

if uncited_refs:
    print(f"\n⚠️ 未引用の文献: {len(uncited_refs)} 件")

if issues:
    print(f"\n⚠️ 要確認の引用: {len(issues)} 件")
    print("\n詳細:")
    for issue in issues:
        print(f"\n[文献 {issue['ref_num']}]")
        print(f"  タイトル: {issue['title'][:80]}...")
        print(f"  文脈（行 {issue['line_num']}）: {issue['context'][:80]}...")
        print(f"  文献キーワード: {', '.join(issue['ref_keywords'])}")
        print(f"  文脈キーワード: {', '.join(issue['context_keywords']) if issue['context_keywords'] else '(未検出)'}")
else:
    print("\n✓ 全ての引用が整合しています（キーワードベースの簡易チェック）")

print("\n" + "=" * 100)
print("注意事項")
print("=" * 100)
print("""
このスクリプトはキーワードベースの簡易チェックです。
最終的な科学的整合性の確認は、以下の方法で行ってください：

1. 各文献のAbstractを読み、本文の記述と一致するか確認
2. PubMed/Google Scholarで文献を検索し、実在することを確認
3. 特に重要な引用（メカニズム、主要結果）は原文を参照
4. 「要確認」とマークされた引用について、手動で整合性を確認

特に注意すべき文献：
- 文脈キーワードが検出されなかった引用（文脈が短い場合）
- 文献キーワードと文脈キーワードが全く重複しない引用
""")
