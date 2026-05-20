#!/usr/bin/env python3
"""Combine all per-source JSON files into a single entries.csv (UTF-8 BOM)."""

import csv
import json
from pathlib import Path

DATA = Path("data")

FIELDS = [
    "source_id",
    "source_org",
    "source_document",
    "source_date",
    "domain",
    "entry_type",
    "original",
    "original_normalized",
    "yasashii",
    "notes",
    "retain_original",
    "is_negative_example",
]

JSON_FILES = sorted(DATA.glob("*.json"))

all_entries = []
for jf in JSON_FILES:
    with open(jf, "r", encoding="utf-8") as f:
        entries = json.load(f)
    print(f"  {jf.name}: {len(entries)} entries")
    all_entries.extend(entries)

print(f"\nTotal: {len(all_entries)} entries from {len(JSON_FILES)} files")

# Write CSV with UTF-8 BOM
out_path = DATA / "entries.csv"
with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    for entry in all_entries:
        writer.writerow(entry)

print(f"Written to {out_path}")

# Verification
from collections import Counter

sources = Counter(e["source_id"] for e in all_entries)
types = Counter(e["entry_type"] for e in all_entries)
domains = Counter(e["domain"] for e in all_entries)
retain = sum(1 for e in all_entries if e["retain_original"])

print(f"\n--- Verification ---")
print(f"Entries by source:")
for sid in sorted(sources.keys()):
    print(f"  {sid}: {sources[sid]}")
print(f"\nEntry types: {dict(types)}")
print(f"Domains: {dict(domains)}")
print(f"retain_original=true: {retain}")

# Check for normalized duplicates across sources
from collections import defaultdict

norm_sources = defaultdict(set)
for e in all_entries:
    if e["original_normalized"]:
        norm_sources[e["original_normalized"]].add(e["source_id"])

multi = {k: v for k, v in norm_sources.items() if len(v) > 1}
print(f"\nTerms appearing in multiple sources: {len(multi)}")
if multi:
    for term, sids in sorted(multi.items(), key=lambda x: -len(x[1]))[:20]:
        print(f"  {term} → sources: {', '.join(sorted(sids))}")
