"""
references.bibから手動番号付きReferencesセクションを生成
"""
import re
from pathlib import Path

# citation_mapの順序（convert_citations.pyの出力から）
citation_order = [
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
]

# references.bibを読み込み
bib_path = Path(__file__).parent.parent / "04_Manuscripts" / "references.bib"
with open(bib_path, 'r', encoding='utf-8') as f:
    bib_content = f.read()

# BibTeXエントリーをパース
entry_pattern = r'@(\w+)\{([^,]+),\s*\n((?:[^@])+)\}'
entries = {}

for match in re.finditer(entry_pattern, bib_content, re.DOTALL):
    entry_type = match.group(1)  # article, misc, book, etc.
    entry_key = match.group(2)   # Yang2020AirPollutionDiabetes, etc.
    fields_text = match.group(3)  # title, author, journal, year, etc.

    # フィールドをパース
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
        # {厚生労働省} などの場合はそのまま
        if author.startswith('{') and author.endswith('}'):
            author = author[1:-1]
        else:
            # 複数著者の場合、最初の著者のみ + et al.
            authors = [a.strip() for a in author.split(' and ')]
            if len(authors) > 3:
                first_author = authors[0].split(',')[0]  # Last name only
                author = f"{first_author} et al."
            elif len(authors) > 1:
                author = ', '.join(authors[:2]) + ' et al.' if len(authors) > 2 else ' and '.join(authors)

    # タイトル
    title = fields.get('title', 'No title')

    # ジャーナル/出版情報
    if entry['type'] == 'article':
        journal = fields.get('journal', '')
        year = fields.get('year', '')
        volume = fields.get('volume', '')
        number = fields.get('number', '')
        pages = fields.get('pages', '')
        doi = fields.get('doi', '')

        # Vancouver形式: Author. Title. Journal. Year;Volume(Number):Pages. doi:DOI
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
        # Web資料
        year = fields.get('year', '')
        note = fields.get('note', '')
        ref = f"{author}. {title}. {year}. {note}"

    elif entry['type'] == 'book':
        publisher = fields.get('publisher', '')
        address = fields.get('address', '')
        year = fields.get('year', '')
        ref = f"{author}. {title}. {publisher}, {address}; {year}"

    else:
        ref = f"{author}. {title}. {fields.get('year', '')}"

    references.append(f"{i}) {ref}")

# Referencesセクションを生成
references_section = "# References\n\n" + "\n\n".join(references)

# ファイルに保存
output_path = Path(__file__).parent.parent / "04_Manuscripts" / "references_manual.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(references_section)

print("References section generated:")
print(output_path)
print(f"\nTotal references: {len(references)}")
