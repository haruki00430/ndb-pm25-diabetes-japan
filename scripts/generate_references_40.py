"""
references.bibから40個の手動番号付きReferencesセクションを生成
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# citation_orderの順序（手動番号順）
citation_order = [
    # 元の25個
    "Yang2020AirPollutionDiabetes",
    "Brook2010ParticulateMatterCVD",
    "Rajagopalan2018AirPollutionCVD",
    "Rajagopalan2019AirPollutionMetabolic",
    "Sun2010AirPollutionInsulinResistance",
    "Eze2015AirPollutionDiabetes",
    "Janghorbani2014AirPollutionDiabetes",
    "Weber2018PM25DiabetesGermany",
    "Bowe2018PM25DiabetesCKD",
    "NIES_PM25_Monitoring",
    "MHLW_NDB_OpenData_No10",
    "Nagashima2021AirPollutionJapanReview",
    "Liu2019PM25T2D_Taiwan",
    "Elliott2013TrafficPMDiabetes",
    "Coogan2012TrafficPMDiabetes",
    "Kim2019PM25DiabetesKorea",
    "Peng2016AirPollutionDiabetesChina",
    "Yang2018PM25MetabolicSyndrome",
    "Wang2014PM25InsulinResistance",
    "Mitsuhashi2019PM25DiabetesOkayama",
    "Ito2023PM25GestationalDiabetesJapan",
    "Morgenstern1995EcologicStudies",
    "Greenland1994EcologicBias",
    "Zeger2000MeasurementError",
    "Anselin1988SpatialEconometrics",
    # 新規15個
    "Yamazaki2021PM25DiabetesJapan",
    "He2019PM25DiabetesComponentsChina",
    "Xu2025UmbrellaReview",
    "Chen2023PM25ComponentsChina",
    "Yang2024PM25ChineseWomen",
    "Adar2023PM25GlycemicMarkersIndia",
    "Riojas-Rodriguez2021PM25MexicoCity",
    "Wang2025TRPV1Mechanism",
    "Mendez2016VascularInsulinResistance",
    "Park2023PM25CircadianDysfunction",
    "Li2019AirPollutionDiabetesReview",
    "Kubo2021PM25CVDJapan",
    "Yorifuji2020PM25HospitalJapan",
    "Bowe2019PM25DiabetesCohortVeterans",
    "Shin2020PM25DiabetesKoreaLongTerm",
]

# references.bibを読み込み
bib_path = Path(__file__).parent.parent / "04_Manuscripts" / "references.bib"
with open(bib_path, 'r', encoding='utf-8') as f:
    bib_content = f.read()

# BibTeXエントリーをパース
entry_pattern = r'@(\w+)\{([^,]+),\s*\n((?:[^@])+)\}'
entries = {}

for match in re.finditer(entry_pattern, bib_content, re.DOTALL):
    entry_type = match.group(1)
    entry_key = match.group(2)
    fields_text = match.group(3)

    fields = {}
    field_pattern = r'(\w+)\s*=\s*\{([^}]+)\}'
    for field_match in re.finditer(field_pattern, fields_text):
        field_name = field_match.group(1)
        field_value = field_match.group(2).strip()
        fields[field_name] = field_value

    entries[entry_key] = {'type': entry_type, 'fields': fields}

# Vancouver形式で文献リストを生成
references = []
for i, key in enumerate(citation_order, 1):
    if key not in entries:
        print(f"Warning: {key} not found in references.bib")
        continue

    entry = entries[key]
    fields = entry['fields']

    # 著者名を処理
    if 'author' in fields:
        author = fields['author']
        if author.startswith('{') and author.endswith('}'):
            author = author[1:-1]
        else:
            authors = [a.strip() for a in author.split(' and ')]
            if len(authors) > 3:
                first_author = authors[0].split(',')[0]
                author = f"{first_author} et al."
            elif len(authors) > 1:
                author = ', '.join([a.split(',')[0] for a in authors[:min(len(authors), 2)]]) + ' et al.' if len(authors) > 2 else ' and '.join([a.split(',')[0] for a in authors])

    title = fields.get('title', 'No title')
    year = fields.get('year', '')

    if entry['type'] == 'article':
        journal = fields.get('journal', '')
        volume = fields.get('volume', '')
        number = fields.get('number', '')
        pages = fields.get('pages', '')
        doi = fields.get('doi', '')

        ref = f"{author}. {title}. {journal}. {year}"
        if volume:
            ref += f";{volume}"
        if number:
            ref += f"({number})"
        if pages:
            ref += f":{pages}"
        if doi:
            ref += f". doi:{doi}"

    elif entry['type'] == 'misc':
        note = fields.get('note', '')
        ref = f"{author}. {title}. {year}. {note}"

    elif entry['type'] == 'book':
        publisher = fields.get('publisher', '')
        address = fields.get('address', '')
        ref = f"{author}. {title}. {publisher}, {address}; {year}"

    else:
        ref = f"{author}. {title}. {year}"

    references.append(f"{i}) {ref}")

# Referencesセクションを生成
references_section = "# References\n\n" + "\n\n".join(references)

# ファイルに保存
output_path = Path(__file__).parent.parent / "04_Manuscripts" / "references_manual_40.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(references_section)

print("✓ References section generated:")
print(f"  Output: {output_path}")
print(f"  Total references: {len(references)}")
print(f"\nFirst 5 references:")
for ref in references[:5]:
    print(f"  {ref[:80]}...")
print(f"\nLast 5 references:")
for ref in references[-5:]:
    print(f"  {ref[:80]}...")
