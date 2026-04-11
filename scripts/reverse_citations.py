"""
手動番号形式を[@...]形式に逆変換するスクリプト
"""
import re
from pathlib import Path

# 元のcitation_map（convert_citations.pyの出力から）
citation_map = {
    1: "Yang2020AirPollutionDiabetes",
    2: "Brook2010ParticulateMatterCVD",
    3: "Rajagopalan2018AirPollutionCVD",
    4: "Rajagopalan2019AirPollutionMetabolic",
    5: "Sun2010AirPollutionInsulinResistance",
    6: "Eze2015AirPollutionDiabetes",
    7: "Janghorbani2014AirPollutionDiabetes",
    8: "Weber2018PM25DiabetesGermany",
    9: "Bowe2018PM25DiabetesCKD",
    10: "NIES_PM25_Monitoring",
    11: "MHLW_NDB_OpenData_No10",
    12: "Nagashima2021AirPollutionJapanReview",
    13: "Liu2019PM25T2D_Taiwan",
    14: "Elliott2013TrafficPMDiabetes",
    15: "Coogan2012TrafficPMDiabetes",
    16: "Kim2019PM25DiabetesKorea",
    17: "Peng2016AirPollutionDiabetesChina",
    18: "Yang2018PM25MetabolicSyndrome",
    19: "Wang2014PM25InsulinResistance",
    20: "Mitsuhashi2019PM25DiabetesOkayama",
    21: "Ito2023PM25GestationalDiabetesJapan",
    22: "Morgenstern1995EcologicStudies",
    23: "Greenland1994EcologicBias",
    24: "Zeger2000MeasurementError",
    25: "Anselin1988SpatialEconometrics",
}

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

def reverse_citation(match):
    """1) -> [@Yang2020...] のように変換"""
    citation_nums = match.group(0).replace(')', '').split(',')
    keys = []
    for num_str in citation_nums:
        num = int(num_str.strip())
        if num in citation_map:
            keys.append(f"@{citation_map[num]}")

    if len(keys) == 1:
        return f"[{keys[0]}]"
    else:
        return f"[{'; '.join(keys)}]"

# 複数引用: 1),2),3) -> [@Key1; @Key2; @Key3]
# 単一引用: 1) -> [@Key1]
# パターン: 数字の羅列（カンマ区切り）+ 閉じ括弧

# 注意: (N = 47) などの統計値と混同しないよう、前後のコンテキストを確認
# 引用は通常、文の末尾や単語の後に来る

# まず、Referencesセクション以前の部分のみ処理
refs_start = content.find("# References")
if refs_start == -1:
    refs_start = len(content)

main_content = content[:refs_start]
refs_content = content[refs_start:]

# 引用パターン: 数字,数字,...) で、前に文字がある場合
# 除外: (N = 数字), (p = 0.数字), など
pattern = r'(?<![(\d])\d+(?:,\d+)*\)'

def is_statistical_value(text, match_pos):
    """統計値かどうかを判定"""
    # 前後20文字を確認
    start = max(0, match_pos - 20)
    end = min(len(text), match_pos + 20)
    context = text[start:end]

    # 除外パターン
    exclude_patterns = [
        r'\(N\s*=\s*\d+\)',
        r'\(n\s*=\s*\d+\)',
        r'p\s*=\s*0\.\d+\)',
        r'HR\s*=\s*\d+\.\d+\)',
        r'OR\s*=\s*\d+\.\d+\)',
        r'β\s*=\s*\d+\)',
        r'CI\s*=\s*\d+',
        r'Volume\s*=\s*\d+',
        r'Number\s*=\s*\d+',
        r'\d+\s*μg/m³',
        r'\d+\s*%',
    ]

    for pattern in exclude_patterns:
        if re.search(pattern, context):
            return True
    return False

# 手動で安全な置換を行う
# まず、全ての引用候補を抽出
matches = list(re.finditer(pattern, main_content))
print(f"Found {len(matches)} potential citation patterns")

# 逆順で置換（後ろから前へ、インデックスがずれないように）
for match in reversed(matches):
    if not is_statistical_value(main_content, match.start()):
        citation_text = reverse_citation(match)
        main_content = main_content[:match.start()] + citation_text + main_content[match.end():]
        print(f"Converted: {match.group()} -> {citation_text}")

# 統合
reversed_content = main_content + refs_content

# 保存
output_path = manuscript_path.parent / "Manuscript_PM25_diabetes_reversed.qmd"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(reversed_content)

print(f"\n✓ Reversed citations saved to: {output_path}")
print(f"  Original format: 1), 2), 3)")
print(f"  Reversed format: [@Yang2020...], [@Brook2010...], ...")
