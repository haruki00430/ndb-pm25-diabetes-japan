"""
安全な参考文献整理スクリプト（プレースホルダ方式）

Step 1: 全引用番号を ##REF_XX## に変換
Step 2: 初登場順を確認し、新番号に置換
Step 3: 未引用文献を追加
Step 4: Referencesセクションを並べ替え
"""
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("Step 1: 引用番号をプレースホルダに変換")
print("=" * 80)

# Referencesセクションを分離
refs_start = content.find("# References")
main_content = content[:refs_start]
refs_content = content[refs_start:]

# 明確な引用パターンのみを対象（文の途中または末尾）
# 例: "pollution 1),2),3)." または "diabetes 4),"

# 既知の引用箇所を手動でリストアップ（check_citations_v2.py の出力から）
known_citations = [
    # Line 51: Introduction
    ('mechanisms including systemic inflammation, oxidative stress, endothelial dysfunction, and insulin resistance 1),2),3),4),5).',
     'mechanisms including systemic inflammation, oxidative stress, endothelial dysfunction, and insulin resistance ##REF_1##,##REF_2##,##REF_3##,##REF_4##,##REF_5##.'),

    ('However, evidence is heterogeneous across settings 6),7),8),9),',
     'However, evidence is heterogeneous across settings ##REF_6##,##REF_7##,##REF_8##,##REF_9##,'),

    # Line 65: Methods
    ('Ambient PM2.5 exposure was derived from national air pollution monitoring data and summarized as the two-year mean (2022–2023) of monitoring-station annual averages within each prefecture 10).',
     'Ambient PM2.5 exposure was derived from national air pollution monitoring data and summarized as the two-year mean (2022–2023) of monitoring-station annual averages within each prefecture ##REF_10##.'),

    # Line 71, 75: Methods
    ('Prefecture-level mean HbA1c (%) was derived from the 10th National Database (NDB) Open Data specific health checkups examination tables (fiscal year 2022) 11).',
     'Prefecture-level mean HbA1c (%) was derived from the 10th National Database (NDB) Open Data specific health checkups examination tables (fiscal year 2022) ##REF_11##.'),

    ('Diabetes medication prescription volume was extracted from the 10th NDB Open Data prescription tables (fiscal year 2023) for therapeutic category 396 and standardized per 100,000 population 11).',
     'Diabetes medication prescription volume was extracted from the 10th NDB Open Data prescription tables (fiscal year 2023) for therapeutic category 396 and standardized per 100,000 population ##REF_11##.'),

    # Line 113: Discussion Section 1
    ('known cardiometabolic effects of air pollution 2),4).',
     'known cardiometabolic effects of air pollution ##REF_2##,##REF_4##.'),

    ('unlikely under current exposure levels in Japan 12).',
     'unlikely under current exposure levels in Japan ##REF_12##.'),

    # Line 117: Discussion Section 2
    ('on the order of a 10–15% increase in diabetes risk per 10 μg/m³ increase in PM2.5 1),6),7),27),28).',
     'on the order of a 10–15% increase in diabetes risk per 10 μg/m³ increase in PM2.5 ##REF_1##,##REF_6##,##REF_7##,##REF_27##,##REF_28##.'),

    ('for type 2 diabetes per 10 μg/m³ increment in PM2.5, with associations varying by region, study design, and exposure range 28).',
     'for type 2 diabetes per 10 μg/m³ increment in PM2.5, with associations varying by region, study design, and exposure range ##REF_28##.'),

    ('elevated diabetes or metabolic risk with increasing fine particulate pollution 13),17),19),29),30),',
     'elevated diabetes or metabolic risk with increasing fine particulate pollution ##REF_13##,##REF_17##,##REF_19##,##REF_29##,##REF_30##,'),

    ('dose-response relationships between PM2.5 and fasting blood glucose 30).',
     'dose-response relationships between PM2.5 and fasting blood glucose ##REF_30##.'),

    ('In India, PM2.5 exposure was significantly associated with glycemic markers and incident diabetes in two large cities 31).',
     'In India, PM2.5 exposure was significantly associated with glycemic markers and incident diabetes in two large cities ##REF_31##.'),

    ('in Mexico and Korea have documented positive PM2.5–diabetes associations in settings with moderate-to-high pollution levels 16),32).',
     'in Mexico and Korea have documented positive PM2.5–diabetes associations in settings with moderate-to-high pollution levels ##REF_16##,##REF_32##.'),

    # Line 118
    ('particularly at lower exposure ranges or in highly adjusted models 8),9).',
     'particularly at lower exposure ranges or in highly adjusted models ##REF_8##,##REF_9##.'),

    # Line 119
    ('in urban settings and gestational diabetes risk 20),21),26),',
     'in urban settings and gestational diabetes risk ##REF_20##,##REF_21##,##REF_26##,'),

    ('have failed to detect statistically significant associations 12).',
     'have failed to detect statistically significant associations ##REF_12##.'),

    ('evaluated using individual-level data and longitudinal designs 26),',
     'evaluated using individual-level data and longitudinal designs ##REF_26##,'),

    # Line 121
    ('endothelial dysfunction, and adipose tissue inflammation 4),5),33),34),35),',
     'endothelial dysfunction, and adipose tissue inflammation ##REF_4##,##REF_5##,##REF_33##,##REF_34##,##REF_35##,'),

    ('outcome definition, and spatial scale 36).',
     'outcome definition, and spatial scale ##REF_36##.'),

    # Line 125
    ('such as diet, socioeconomic status, or family history 22),23).',
     'such as diet, socioeconomic status, or family history ##REF_22##,##REF_23##.'),

    ('compared with individual-level exposure assessment 24).',
     'compared with individual-level exposure assessment ##REF_24##.'),

    # Line 127
    ('particularly when the number and spatial distribution of monitors are uneven 24).',
     'particularly when the number and spatial distribution of monitors are uneven ##REF_24##.'),

    # Line 129
    ('with true diabetes prevalence or control 11).',
     'with true diabetes prevalence or control ##REF_11##.'),

    # Line 131
    ('of chronic disease risk 22),25).',
     'of chronic disease risk ##REF_22##,##REF_25##.'),

    # Line 133
    ('(e.g., municipalities or secondary medical areas). For these reasons, the null findings should be interpreted as reflecting the limitations of ecological design and data structure rather than evidence that PM2.5 is metabolically harmless.',
     '(e.g., municipalities or secondary medical areas). For these reasons, the null findings should be interpreted as reflecting the limitations of ecological design and data structure rather than evidence that PM2.5 is metabolically harmless.'),

    # Line 137
    ('identified in ecological and spatial epidemiology 22),25).',
     'identified in ecological and spatial epidemiology ##REF_22##,##REF_25##.'),

    ('but sometimes crossed the null due to limited power and correlated covariates 8),9).',
     'but sometimes crossed the null due to limited power and correlated covariates ##REF_8##,##REF_9##.'),

    # Line 141: Section 4
    ('induce local oxidative stress and inflammation 35).',
     'induce local oxidative stress and inflammation ##REF_35##.'),

    ('including adipose tissue, skeletal muscle, liver, and pancreatic β-cells 33).',
     'including adipose tissue, skeletal muscle, liver, and pancreatic β-cells ##REF_33##.'),

    ('through pulmonary oxidative stress 34),',
     'through pulmonary oxidative stress ##REF_34##,'),

    ('and systemic oxidative stress 35).',
     'and systemic oxidative stress ##REF_35##.'),

    ('as a diabetogenic environmental risk factor 4),5).',
     'as a diabetogenic environmental risk factor ##REF_4##,##REF_5##.'),

    # Line 145: Section 5
    ('and urban–rural differences 10),11).',
     'and urban–rural differences ##REF_10##,##REF_11##.'),

    ('relative to those showing clear risk elevations 1),6),7);',
     'relative to those showing clear risk elevations ##REF_1##,##REF_6##,##REF_7##;'),

    # Line 149: Section 6
    ('and limited ability to detect small effects given the fixed number of prefectures 22),23),24).',
     'and limited ability to detect small effects given the fixed number of prefectures ##REF_22##,##REF_23##,##REF_24##.'),

    ('even when underlying biologic effects exist 12),13),31).',
     'even when underlying biologic effects exist ##REF_12##,##REF_13##,##REF_31##.'),

    # Line 155: Section 7
    ('to reduce spatial misalignment 24),25).',
     'to reduce spatial misalignment ##REF_24##,##REF_25##.'),

    ('from Asia and other regions 13),16),17),18),26),29),30).',
     'from Asia and other regions ##REF_13##,##REF_16##,##REF_17##,##REF_18##,##REF_26##,##REF_29##,##REF_30##.'),

    # Line 157
    ('from experimental studies 4),5),29),33),35).',
     'from experimental studies ##REF_4##,##REF_5##,##REF_29##,##REF_33##,##REF_35##.'),

    ('could refine risk estimates 29).',
     'could refine risk estimates ##REF_29##.'),

    # Line 159
    ('from air quality improvements 1),6),12),36),39).',
     'from air quality improvements ##REF_1##,##REF_6##,##REF_12##,##REF_36##,##REF_39##.'),
]

modified_content = main_content
conversion_count = 0

for old_text, new_text in known_citations:
    if old_text in modified_content:
        modified_content = modified_content.replace(old_text, new_text)
        conversion_count += 1
        # 変換された箇所を表示（最初の50文字）
        print(f"✓ {old_text[:50]}... → プレースホルダに変換")

print(f"\n合計 {conversion_count} 箇所を変換しました")

# プレースホルダ版を保存
placeholder_content = modified_content + refs_content
placeholder_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes_placeholder.qmd"
with open(placeholder_path, 'w', encoding='utf-8') as f:
    f.write(placeholder_content)

print(f"\n✓ プレースホルダ版を保存: {placeholder_path}")

print("\n" + "=" * 80)
print("Step 2: プレースホルダを確認し、次のステップを計画")
print("=" * 80)

# プレースホルダを抽出
placeholder_pattern = r'##REF_(\d+)##'
found_refs = set()
for match in re.finditer(placeholder_pattern, modified_content):
    found_refs.add(int(match.group(1)))

print(f"\n検出されたプレースホルダ: {sorted(found_refs)}")
print(f"総数: {len(found_refs)}")

# 未変換の引用番号がないか確認
remaining_pattern = r'(?<=[a-zA-Z\s\.])\d+\)(?:,\s*\d+\))*'
remaining_citations = []
for line in modified_content.split('\n'):
    if any(pattern in line for pattern in ['(N = ', 'p = ', 'β = ', '| ']):
        continue
    for match in re.finditer(remaining_pattern, line):
        context = line[max(0, match.start()-40):match.end()+40]
        if '=' not in context and '±' not in context:
            remaining_citations.append((line.strip()[:80], match.group()))

if remaining_citations:
    print("\n⚠️ 警告: まだプレースホルダに変換されていない引用があります:")
    for line_text, citation in remaining_citations[:10]:
        print(f"  {citation} in: {line_text}...")

print("\n次のステップ:")
print("1. Manuscript_PM25_diabetes_placeholder.qmd を確認")
print("2. 初登場順にプレースホルダを検出")
print("3. プレースホルダを新番号に置換")
print("4. Referencesセクションを並べ替え")
