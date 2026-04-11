"""
PM25_diabetes原稿の引用を[@...]形式から手動番号形式に変換するスクリプト
"""
import re
from pathlib import Path

# 引用の登場順序を記録する辞書
citation_map = {}
citation_counter = 1

# 原稿ファイルを読み込み
manuscript_path = Path(__file__).parent.parent / "04_Manuscripts" / "Manuscript_PM25_diabetes.qmd"
with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# [@...] 形式の引用を全て抽出
# 複数引用のパターン: [@Author1; @Author2; @Author3]
# 単一引用のパターン: [@Author]
citation_pattern = r'\[@([^\]]+)\]'

def process_citation_block(match):
    """[@Author1; @Author2] を [1,2] に変換"""
    global citation_counter
    citation_text = match.group(1)

    # セミコロンで区切って個別の引用キーを抽出
    citation_keys = [k.strip().lstrip('@') for k in citation_text.split(';')]

    # 各キーに番号を割り当て（初出時のみ）
    numbers = []
    for key in citation_keys:
        if key not in citation_map:
            citation_map[key] = citation_counter
            citation_counter += 1
        numbers.append(str(citation_map[key]))

    # 番号リストを文字列に変換
    # 単一引用: 1)  複数引用: 1),2),3)
    if len(numbers) == 1:
        return f"{numbers[0]})"
    else:
        return ','.join([f"{n})" for n in numbers])

# 引用を順次処理
content_converted = re.sub(citation_pattern, process_citation_block, content)

# 引用マップを出力（デバッグ用）
print("=== Citation Mapping ===")
for key, num in sorted(citation_map.items(), key=lambda x: x[1]):
    print(f"{num:2d}. {key}")

# 変換後のファイルを一時保存
output_path = manuscript_path.parent / "Manuscript_PM25_diabetes_converted.qmd"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content_converted)

print(f"\n変換完了: {output_path}")
print(f"総引用数: {citation_counter - 1}")
