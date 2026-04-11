"""
引用内容の科学的整合性を確認するスクリプト
各引用箇所の文脈と、引用されている論文の内容が一致しているかチェックする
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルとReferencesを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Referencesセクションを抽出
refs_start = content.find("# References")
refs_section = content[refs_start:]

# 各文献のタイトルとキーワードを抽出
ref_pattern = r'^(\d+)\) (.+?)\. (.+?)\. (.+?)\. (\d{4})'
references = {}

for match in re.finditer(ref_pattern, refs_section, re.MULTILINE):
    num = int(match.group(1))
    authors = match.group(2)
    title = match.group(3)
    journal = match.group(4)
    year = match.group(5)

    references[num] = {
        'authors': authors,
        'title': title,
        'journal': journal,
        'year': year
    }

print("=" * 80)
print("引用内容の科学的整合性チェック")
print("=" * 80)

# チェックすべき主要な引用箇所と期待される内容
citation_checks = [
    {
        'context': 'mechanisms including systemic inflammation, oxidative stress, endothelial dysfunction, and insulin resistance',
        'citations': [1, 2, 3, 4, 5],
        'expected_keywords': ['inflammation', 'oxidative', 'metabolic', 'insulin resistance', 'cardiovascular'],
        'section': 'Introduction'
    },
    {
        'context': 'evidence is heterogeneous across settings',
        'citations': [6, 7, 8, 9],
        'expected_keywords': ['meta-analysis', 'systematic review', 'diabetes', 'null', 'borderline'],
        'section': 'Introduction'
    },
    {
        'context': 'known cardiometabolic effects of air pollution',
        'citations': [2, 4],
        'expected_keywords': ['cardiovascular', 'metabolic', 'PM2.5', 'pollution'],
        'section': 'Discussion Section 1'
    },
    {
        'context': 'Several recent meta-analyses have documented modest but statistically significant associations',
        'citations': [1, 6, 7, 13, 14],
        'expected_keywords': ['meta-analysis', 'systematic review', 'diabetes', 'PM2.5'],
        'section': 'Discussion Section 2'
    },
    {
        'context': 'Large cohort studies from heavily polluted Asian settings',
        'citations': [15, 16, 17, 18, 19],
        'expected_keywords': ['China', 'cohort', 'diabetes', 'PM2.5', 'Asia'],
        'section': 'Discussion Section 2'
    },
    {
        'context': 'PM2.5 exposure was significantly associated with glycemic markers and incident diabetes in two large Indian cities',
        'citations': [20],
        'expected_keywords': ['India', 'glycemic', 'diabetes', 'PM2.5'],
        'section': 'Discussion Section 2'
    },
    {
        'context': 'in Mexico and Korea have documented positive PM2.5–diabetes associations',
        'citations': [21, 22],
        'expected_keywords': ['Mexico', 'Korea', 'diabetes', 'PM2.5'],
        'section': 'Discussion Section 2'
    },
    {
        'context': 'null or borderline associations, particularly at lower exposure ranges',
        'citations': [8, 9, 23, 24],
        'expected_keywords': ['null', 'no association', 'Germany', 'Europe', 'North America'],
        'section': 'Discussion Section 2'
    },
    {
        'context': 'Within Japan, both individual-level and area-level studies have documented positive associations',
        'citations': [25, 26, 27],
        'expected_keywords': ['Japan', 'diabetes', 'PM2.5', 'Okayama', 'gestational', 'Tokyo'],
        'section': 'Discussion Section 2'
    },
    {
        'context': 'PM2.5 is biologically capable of impairing glucose metabolism through pathways such as systemic inflammation, oxidative stress, endothelial dysfunction, and adipose tissue inflammation',
        'citations': [4, 5, 28, 29, 30],
        'expected_keywords': ['mechanism', 'inflammation', 'oxidative', 'insulin', 'glucose'],
        'section': 'Discussion Section 2'
    },
    {
        'context': 'ecological fallacy and within-prefecture heterogeneity',
        'citations': [32, 33],
        'expected_keywords': ['ecological', 'bias', 'fallacy', 'confounding'],
        'section': 'Discussion Section 3'
    },
    {
        'context': 'measurement error, which tends to attenuate concentration–response relationships',
        'citations': [34],
        'expected_keywords': ['measurement error', 'exposure', 'bias'],
        'section': 'Discussion Section 3'
    },
    {
        'context': 'PM2.5 particles deposit in the lung alveoli and induce local oxidative stress and inflammation',
        'citations': [30],
        'expected_keywords': ['oxidative', 'lung', 'inflammation', 'PM2.5'],
        'section': 'Discussion Section 4'
    },
    {
        'context': 'transient receptor potential vanilloid 1 (TRPV1) pathway as a key mediator',
        'citations': [28],
        'expected_keywords': ['TRPV1', 'mechanism', 'pathway', 'receptor'],
        'section': 'Discussion Section 4'
    },
    {
        'context': 'PM2.5 exposure induces vascular insulin resistance through pulmonary oxidative stress',
        'citations': [29],
        'expected_keywords': ['vascular', 'insulin resistance', 'pulmonary', 'oxidative'],
        'section': 'Discussion Section 4'
    },
]

print(f"\n総チェック数: {len(citation_checks)}")
print("\n" + "=" * 80)

issues = []
verified = 0

for i, check in enumerate(citation_checks, 1):
    print(f"\n[チェック {i}/{len(citation_checks)}] {check['section']}")
    print(f"文脈: {check['context'][:80]}...")
    print(f"引用: {check['citations']}")

    # 各引用文献を確認
    all_match = True
    for cite_num in check['citations']:
        if cite_num in references:
            ref = references[cite_num]
            title_lower = ref['title'].lower()
            authors_lower = ref['authors'].lower()

            # キーワードマッチをチェック
            found_keywords = []
            for keyword in check['expected_keywords']:
                if keyword.lower() in title_lower or keyword.lower() in authors_lower:
                    found_keywords.append(keyword)

            # 最低1つのキーワードが一致すれば OK
            if len(found_keywords) == 0:
                all_match = False
                issues.append({
                    'check_num': i,
                    'citation': cite_num,
                    'context': check['context'][:60],
                    'title': ref['title'],
                    'reason': f"期待されるキーワード {check['expected_keywords'][:3]}... が見つかりません"
                })
                print(f"  ⚠️ {cite_num}) {ref['authors']} ({ref['year']})")
                print(f"     タイトル: {ref['title'][:60]}...")
                print(f"     → キーワード不一致")
            else:
                print(f"  ✓ {cite_num}) {ref['authors']} ({ref['year']}) - {', '.join(found_keywords[:2])}")

    if all_match:
        verified += 1

print("\n" + "=" * 80)
print("検証結果サマリー")
print("=" * 80)

print(f"\n✓ 検証済み: {verified}/{len(citation_checks)} ({verified/len(citation_checks)*100:.1f}%)")

if issues:
    print(f"\n⚠️ 要確認: {len(issues)} 件")
    print("\n詳細:")
    for issue in issues:
        print(f"\n[チェック {issue['check_num']}] 引用 {issue['citation']}")
        print(f"  文脈: {issue['context']}...")
        print(f"  タイトル: {issue['title']}")
        print(f"  理由: {issue['reason']}")
else:
    print("\n✓ 全ての引用が科学的に整合しています")

print("\n" + "=" * 80)
print("注意事項")
print("=" * 80)
print("""
このスクリプトはキーワードベースの簡易チェックです。
最終的な科学的整合性の確認は、以下の方法で行ってください：

1. 各文献のAbstractを読み、本文の記述と一致するか確認
2. PubMed/Google Scholarで文献を検索し、実在することを確認
3. 特に重要な引用（メカニズム、主要結果）は原文を参照
""")
