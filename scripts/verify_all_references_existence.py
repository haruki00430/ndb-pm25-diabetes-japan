"""
全文献の実在性と内容の整合性をチェックするスクリプト
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 100)
print("全文献の実在性と内容の整合性チェック")
print("=" * 100)

# Referencesセクションを分離
refs_start = content.find("# References")
refs_section = content[refs_start:]

# ===== Step 1: References セクションから全文献を抽出 =====
print("\n[Step 1] References セクションから全文献を抽出\n")

# 文献パターン（番号、著者、タイトル、ジャーナル、年、DOI）
ref_pattern = r'^(\d+)\) (.+?)\.(.+?)\.(.+?)\. (\d{4})'
references = {}
ref_lines = []

for line_num, line in enumerate(refs_section.split('\n'), 1):
    match = re.match(ref_pattern, line)
    if match:
        num = int(match.group(1))
        authors = match.group(2).strip()
        title = match.group(3).strip()
        journal = match.group(4).strip()
        year = match.group(5).strip()

        # DOIを抽出
        doi_match = re.search(r'doi:(10\.\S+)', line)
        doi = doi_match.group(1) if doi_match else None

        references[num] = {
            'authors': authors,
            'title': title,
            'journal': journal,
            'year': year,
            'doi': doi,
            'full_text': line
        }
        ref_lines.append(num)

print(f"✓ 抽出した文献数: {len(references)}")
print(f"✓ 文献番号: {sorted(references.keys())}\n")

# ===== Step 2: 欠番のチェック =====
print("\n[Step 2] 欠番のチェック\n")

all_nums = sorted(references.keys())
if all_nums:
    expected_nums = set(range(1, max(all_nums) + 1))
    actual_nums = set(all_nums)
    missing_nums = sorted(expected_nums - actual_nums)

    if missing_nums:
        print(f"⚠️ 欠番が {len(missing_nums)} 件あります: {missing_nums}")
    else:
        print("✓ 欠番はありません（1から連番）")

# ===== Step 3: 各文献の詳細表示 =====
print("\n[Step 3] 各文献の詳細とチェック項目\n")
print("=" * 100)

issues = []

for num in sorted(references.keys()):
    ref = references[num]
    print(f"\n[{num}] {ref['authors']} ({ref['year']})")
    print(f"タイトル: {ref['title']}")
    print(f"ジャーナル: {ref['journal']}")
    print(f"DOI: {ref['doi'] if ref['doi'] else '❌ なし'}")

    # チェック項目
    checks = []

    # 1. タイトルに "diabetes" または "metabolic" が含まれているか
    title_lower = ref['title'].lower()
    has_diabetes = 'diabetes' in title_lower or 'diabetic' in title_lower
    has_metabolic = 'metabolic' in title_lower or 'glucose' in title_lower or 'insulin' in title_lower
    has_pm25 = 'pm2.5' in title_lower or 'particulate' in title_lower or 'air pollution' in title_lower

    if not (has_diabetes or has_metabolic or has_pm25):
        checks.append("⚠️ タイトルに diabetes/metabolic/PM2.5 が含まれていません")

    # 2. 年が妥当か（1990-2026年）
    year_int = int(ref['year'])
    if year_int < 1990 or year_int > 2026:
        checks.append(f"⚠️ 年が範囲外: {ref['year']}")

    # 3. DOIの形式が妥当か
    if ref['doi']:
        if not ref['doi'].startswith('10.'):
            checks.append(f"⚠️ DOI形式が不正: {ref['doi']}")
    else:
        # 日本政府機関のデータは DOI なしでも OK
        if 'National Institute' not in ref['authors'] and 'Ministry of' not in ref['authors']:
            checks.append("⚠️ DOI がありません")

    # 4. 著者名の形式チェック
    if 'et al.' not in ref['authors'] and ',' not in ref['authors']:
        # 単著の可能性（稀）
        if 'National Institute' not in ref['authors'] and 'Ministry of' not in ref['authors']:
            checks.append("⚠️ 著者名の形式が単著のようです")

    # チェック結果を表示
    if checks:
        for check in checks:
            print(f"  {check}")
        issues.append({
            'num': num,
            'title': ref['title'],
            'checks': checks
        })
    else:
        print("  ✓ 基本的なチェックに問題なし")

# ===== Step 4: 特定の文献の詳細チェック =====
print("\n" + "=" * 100)
print("[Step 4] 特定の文献の詳細チェック")
print("=" * 100)

# 重要な文献（メタアナリシス、日本の研究）を確認
important_refs = [1, 4, 5, 6, 8, 9, 10, 11, 12]

print("\n重要な文献の確認:\n")

for num in important_refs:
    if num in references:
        ref = references[num]
        print(f"[{num}] {ref['authors']} ({ref['year']})")
        print(f"  タイトル: {ref['title'][:80]}...")

        # タイプを推定
        title_lower = ref['title'].lower()
        if 'meta-analysis' in title_lower or 'systematic review' in title_lower:
            print(f"  タイプ: メタアナリシス / システマティックレビュー")
        elif 'cohort' in title_lower or 'longitudinal' in title_lower:
            print(f"  タイプ: コホート研究")
        elif 'japan' in title_lower or 'japanese' in title_lower:
            print(f"  タイプ: 日本の研究")
        elif 'National Institute' in ref['authors'] or 'Ministry of' in ref['authors']:
            print(f"  タイプ: 政府データ")
        else:
            print(f"  タイプ: その他")
        print()

# ===== Step 5: サマリー =====
print("\n" + "=" * 100)
print("サマリー")
print("=" * 100)

print(f"\n✓ 総文献数: {len(references)}")
print(f"✓ 番号範囲: {min(references.keys()) if references else 'N/A'} - {max(references.keys()) if references else 'N/A'}")

if missing_nums:
    print(f"\n⚠️ 欠番: {missing_nums}")

if issues:
    print(f"\n⚠️ 要確認の文献: {len(issues)} 件")
    print("\n詳細:")
    for issue in issues:
        print(f"\n[{issue['num']}] {issue['title'][:60]}...")
        for check in issue['checks']:
            print(f"  {check}")
else:
    print("\n✓ 全ての文献が基本的なチェックをパスしました")

print("\n" + "=" * 100)
print("次のステップ")
print("=" * 100)
print("""
1. 欠番（7番）の原因を確認し、必要に応じて文献を追加または番号を繰り上げ
2. 要確認の文献について、PubMed/Google Scholarで実在を確認
3. 各文献のタイトル・著者・年・DOIが正確か原文で確認
4. 引用箇所の文脈と文献の内容が一致しているか確認
""")
