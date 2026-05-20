#!/usr/bin/env python3
"""Extract MATCHA parallel corpus into per-source JSON."""

import json
from pathlib import Path

SOURCES = Path("sources")
DATA = Path("data")
DATA.mkdir(exist_ok=True)

MATCHA_DIR = SOURCES / "matcha_repo"


def extract_matcha():
    """Extract Source 23: MATCHA やさしい日本語パラレルコーパス (16,000 sentence pairs)."""
    comp_path = MATCHA_DIR / "matcha.comp"
    simp_path = MATCHA_DIR / "matcha.simp"
    tag_path = MATCHA_DIR / "matcha.tag"

    with open(comp_path, "r", encoding="utf-8") as f_comp, \
         open(simp_path, "r", encoding="utf-8") as f_simp, \
         open(tag_path, "r", encoding="utf-8") as f_tag:
        comp_lines = f_comp.read().splitlines()
        simp_lines = f_simp.read().splitlines()
        tag_lines = f_tag.read().splitlines()

    assert len(comp_lines) == len(simp_lines) == len(tag_lines), (
        f"Line count mismatch: comp={len(comp_lines)}, simp={len(simp_lines)}, tag={len(tag_lines)}"
    )

    entries = []
    skipped = 0
    for comp, simp, tag in zip(comp_lines, simp_lines, tag_lines):
        if comp.strip() == simp.strip():
            skipped += 1
            continue
        entries.append({
            "source_id": "23",
            "source_org": "愛媛大学",
            "source_document": "MATCHA やさしい日本語パラレルコーパス",
            "source_date": "2024",
            "domain": "日常生活",
            "entry_type": "sentence",
            "original": comp,
            "original_normalized": comp,
            "yasashii": simp,
            "notes": tag,
            "retain_original": False,
            "is_negative_example": False,
        })

    out_path = DATA / "23_matcha.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"23_MATCHA: {len(entries)} entries → {out_path} (skipped {skipped} identical pairs)")
    return entries


if __name__ == "__main__":
    extract_matcha()
