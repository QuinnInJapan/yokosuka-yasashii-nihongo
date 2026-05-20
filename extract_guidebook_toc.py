#!/usr/bin/env python3
"""Extract aligned TOC heading pairs from source 20 (ISA Living Guide)."""

import json
from pathlib import Path

DATA = Path("data")
DATA.mkdir(exist_ok=True)

ALIGNMENT = Path("sources/20_出入国在留管理庁_ガイドブック/toc_alignment.json")


def extract_toc_pairs():
    with open(ALIGNMENT, "r", encoding="utf-8") as f:
        alignment = json.load(f)

    sections = alignment["sections"]
    entries = []

    for sec in sections:
        orig = sec.get("original")
        yasa = sec.get("yasashii")

        # Skip if either side is missing or they're identical
        if not orig or not yasa:
            continue
        if orig == yasa:
            continue

        entries.append({
            "source_id": "20",
            "source_org": "出入国在留管理庁",
            "source_document": "生活・就労ガイドブック／生活・仕事ガイドブック",
            "source_date": "2026",
            "domain": "日常生活",
            "entry_type": "term",
            "original": orig,
            "original_normalized": orig,
            "yasashii": yasa,
            "notes": f"見出し {sec['id']}",
            "retain_original": False,
            "is_negative_example": False,
        })

    out_path = DATA / "20_guidebook.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"20_guidebook: {len(entries)} TOC heading pairs → {out_path}")
    return entries


if __name__ == "__main__":
    extract_toc_pairs()
