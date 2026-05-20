#!/usr/bin/env python3
"""Extract data from the 3 already-structured sources (02, 03, 12) into per-source JSON."""

import csv
import json
import re
import pandas as pd
from pathlib import Path

SOURCES = Path("sources")
DATA = Path("data")
DATA.mkdir(exist_ok=True)


def strip_html(text: str) -> str:
    """Replace <br> tags with ／ and remove any remaining HTML tags."""
    s = re.sub(r'<br\s*/?>', '／', text, flags=re.IGNORECASE)
    s = re.sub(r'<[^>]+>', '', s)
    return s


def normalize_original(text: str) -> str:
    """Normalize original text for consensus matching.

    Rules:
    1. Strip ISA variant markers: 初診(1) → 初診
    2. Strip furigana parentheses: 危(あぶ)ない → 危ない
    3. Strip angle-bracket glosses: 津波＜とても高い波＞ → 津波
    4. Strip ＊ markers
    5. Collapse whitespace
    6. Remove leading/trailing whitespace
    """
    s = text
    # Strip ISA variant markers like (1), (2), (3)
    s = re.sub(r'\((\d+)\)', '', s)
    s = re.sub(r'（(\d+)）', '', s)
    # Strip furigana in parentheses: kanji(hiragana) patterns
    # Match: kanji char(s) followed by (hiragana+)
    s = re.sub(r'（[ぁ-ゖー]+）', '', s)
    s = re.sub(r'\([ぁ-ゖー]+\)', '', s)
    # Strip angle-bracket glosses ＜...＞
    s = re.sub(r'＜[^＞]*＞', '', s)
    # Strip ＊ markers
    s = s.replace('＊', '').replace('*', '')
    # Collapse whitespace
    s = re.sub(r'\s+', ' ', s)
    # Strip leading/trailing
    s = s.strip()
    return s


def extract_02_isa():
    """Extract Source 02: ISA 書き換えツール語彙データ (CSV, 925 entries)."""
    entries = []
    csv_path = SOURCES / "02_出入国在留管理庁" / "書き換えツール_語彙データ.csv"

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original = strip_html(row['original'].strip())
            yasashii = strip_html(row['yasashii'].strip())
            entries.append({
                "source_id": "02",
                "source_org": "出入国在留管理庁",
                "source_document": "やさしい日本語書き換えツール 語彙データ",
                "source_date": "2020",
                "domain": "",
                "entry_type": "term",
                "original": original,
                "original_normalized": normalize_original(original),
                "yasashii": yasashii,
                "notes": "",
                "retain_original": False,
                "is_negative_example": False,
            })

    out_path = DATA / "02_isa.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"02_ISA: {len(entries)} entries → {out_path}")
    return entries


def extract_03_hirosaki():
    """Extract Source 03: 弘前大学 災害基礎語彙 (2 CSVs, 200 entries total)."""
    entries = []

    for csv_name in ["地震災害基礎語彙100.csv", "大雨_洪水_土砂災害基礎語彙100.csv"]:
        csv_path = SOURCES / "03_弘前大学" / csv_name
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                original = row['original'].strip()
                yasashii = row['yasashii'].strip()
                level = row.get('level', '').strip()

                # Check for ＊ marker → retain_original
                retain = '＊' in yasashii

                notes = f"JLPT: {level}" if level else ""

                entries.append({
                    "source_id": "03",
                    "source_org": "弘前大学",
                    "source_document": "災害基礎語彙集成",
                    "source_date": "2013",
                    "domain": "防災",
                    "entry_type": "term",
                    "original": original,
                    "original_normalized": normalize_original(original),
                    "yasashii": yasashii,
                    "notes": notes,
                    "retain_original": retain,
                    "is_negative_example": False,
                })

    out_path = DATA / "03_hirosaki.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"03_弘前大学: {len(entries)} entries → {out_path}")
    return entries


def extract_12_yokohama():
    """Extract Source 12: 横浜市 語彙集 (XLSX, 561 entries)."""
    xlsx_path = SOURCES / "12_横浜市" / "語彙集.xlsx"

    # Read without header, data starts at row 4 (0-indexed)
    df = pd.read_excel(xlsx_path, engine='openpyxl', header=None)

    # Columns: 0=あいうえお section header, 1=No., 2=語彙, 3=分野, 4=意味
    # Data starts at row index 4 (after title, description, blank, header rows)

    # Domain mapping: 横浜市 分野 → controlled vocabulary
    domain_map = {
        '防災・救急': '防災',
        '届出・申請': '行政手続',
        '保険・年金': '社会保険',
        '健康・福祉': '医療',
        '子育て・教育': '教育',
        '暮らし': '日常生活',
        'ごみ・リサイクル': '日常生活',
        '税金': '行政手続',
        '住まい': '日常生活',
        '仕事': '日常生活',
    }

    entries = []
    for idx in range(4, len(df)):
        row = df.iloc[idx]
        no_val = row[1]
        goi = row[2]
        bunya = row[3]
        imi = row[4]

        # Skip rows without a vocab entry
        if pd.isna(goi) or pd.isna(imi):
            continue

        goi = str(goi).strip()
        imi = str(imi).strip()
        bunya_str = str(bunya).strip() if not pd.isna(bunya) else ""

        if not goi or not imi:
            continue

        # Map domain
        domain = domain_map.get(bunya_str, 'その他')

        entries.append({
            "source_id": "12",
            "source_org": "横浜市",
            "source_document": "やさしい日本語で伝える 語彙集",
            "source_date": "2024",
            "domain": domain,
            "entry_type": "term",
            "original": goi,
            "original_normalized": normalize_original(goi),
            "yasashii": imi,
            "notes": f"分野: {bunya_str}" if bunya_str else "",
            "retain_original": False,
            "is_negative_example": False,
        })

    out_path = DATA / "12_yokohama.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"12_横浜市: {len(entries)} entries → {out_path}")
    return entries


if __name__ == "__main__":
    all_entries = []
    all_entries.extend(extract_02_isa())
    all_entries.extend(extract_03_hirosaki())
    all_entries.extend(extract_12_yokohama())
    print(f"\nPhase 1 total: {len(all_entries)} entries")
