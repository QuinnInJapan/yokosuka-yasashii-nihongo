# Project: やさしい日本語 Precedent Reference System

## Source metadata

When adding a new source (new JSON file under `data/`), **always add a corresponding row to `data/sources.csv`** with:
- `source_id` — numeric ID matching the JSON filename prefix (e.g., `21` for `21_clair.json`)
- `source_org` — issuing organization (must match `source_org` in the JSON entries)
- `source_document` — document title (must match `source_document` in the JSON entries)
- `source_url` — direct URL to the PDF/page/download
- `source_date` — publication year (leave blank if unknown)

This file is the single source of truth for source URLs and must stay in sync with the data files.
