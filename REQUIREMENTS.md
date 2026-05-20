# Requirements Document
## やさしい日本語 Precedent Reference System
**Version 0.3**

---

## 1. Problem Statement

Staff at our 市役所 must produce やさしい日本語 materials but lack a shared standard. Debates arise around vocabulary choice, expression level, and naturalness because there is no authoritative internal reference. The goal of this system is not to create a new standard from scratch, but to surface and organize existing standards and examples from other government entities — enabling 前例主義-style decisions that are fast, defensible, and consistent.

---

## 2. Goals

| # | Goal |
|---|------|
| G1 | Allow staff to find how a given term or phrase has been handled in official government やさしい日本語 materials |
| G2 | Make the breadth and consensus of existing examples legible at a glance — so staff can judge whether a given choice is common or idiosyncratic |
| G3 | Surface the authoritative source of each example so decisions can be attributed to a 前例 |
| G4 | Reduce per-document debate time by giving staff a lookup workflow before any internal discussion begins |

---

## 3. Users

**Primary user:** Municipal staff member drafting or reviewing a やさしい日本語 document (no specialized linguistics background assumed).

**Secondary user:** Section lead or supervisor who needs to sign off on a やさしい日本語 choice and wants a defensible 前例.

---

## 4. Core Use Cases

### UC-1: Term lookup
> "How do other governments express 避難指示 in やさしい日本語?"

User inputs a term. System returns:
- All attested やさしい日本語 renderings of that term across sources
- The source document and issuing entity for each
- How many sources use each rendering (so consensus is visible)

### UC-2: Sentence keyword search
> "We're writing about 届出. What do existing sentences using that word look like?"

User inputs a keyword. System returns all sentence-level entries whose `original` or `yasashii` field contains the keyword, with source attribution.

*Note: This is keyword matching, not fuzzy similarity. Full sentence similarity would require embeddings or morphological analysis and is out of scope for v1.*

### UC-3: Topic browse
> "We're writing about 台風 evacuation. What does existing official material in this area look like?"

User filters by topic/domain. System returns term–rendering pairs and sentence examples in that topic area, with sources.

*Note: Domain assignment is approximate — entries may span multiple topics. Staff should use keyword search (UC-2) as the primary lookup method and treat domain filtering as a secondary browse tool.*

### UC-4: Source browse
> "What has 川崎市 published on this?"

User filters by issuing entity or document to understand the full scope of a particular organization's やさしい日本語 choices.

---

## 5. Data Requirements

### 5.1 Schema

Each row represents one entry — a term pair or sentence pair from a source document.

| Field | Description |
|---|---|
| `source_org` | Issuing organization, e.g. 川崎市 |
| `source_document` | Document title |
| `source_url` | Direct URL to the PDF or page |
| `source_date` | Publication year |
| `domain` | Topic area — see controlled vocabulary in §5.4. Comma-separated if multiple apply. |
| `entry_type` | `term`, `sentence`, or `paragraph` |
| `original` | Original Japanese text |
| `original_normalized` | Kanji-only normalized form for consensus counting (no furigana, no parentheticals) |
| `yasashii` | やさしい日本語 rendering |
| `notes` | Any explanatory gloss from the source document |
| `retain_original` | Boolean — whether the source instructs to keep the original term and append an explanation, rather than replace it |
| `is_negative_example` | Boolean — whether this is a "before" example marked as problematic, rather than a recommended rendering |

### 5.2 Note on `retain_original`

Some terms (e.g. 津波, 避難) are explicitly marked in national guidelines as terms to *retain* in their original form, with a plain-language explanation appended rather than a substitution. This distinction is important for staff decisions and should be captured as a dedicated field rather than buried in `notes`.

### 5.3 Note on `original_normalized`

The `consensus` view counts how many sources use each rendering for a given original term. For this to work, the original must be normalized — if one source writes `避難指示` and another writes `避難指示（ひなんしじ）`, they need to match. `original_normalized` strips furigana, parentheticals, and whitespace so the pivot works cleanly.

### 5.4 Domain controlled vocabulary

Use these values for the `domain` field. An entry may have multiple comma-separated values.

- `防災` — disaster preparedness and response
- `避難` — evacuation
- `行政手続` — administrative procedures
- `在留` — residency and immigration
- `社会保険` — social insurance and pensions
- `医療` — healthcare
- `教育` — education
- `日常生活` — general daily life
- `その他` — anything that doesn't fit above

### 5.5 Sources

The corpus draws from published government やさしい日本語 materials. Sources are tiered by priority — the system is useful once all Essential and most High sources are loaded.

**Each source must be verified as downloadable before work begins.** If a source can't be found in 5 minutes of searching, demote it to Desirable.

| Priority | Source | Entry type | Notes |
|----------|--------|------------|-------|
| 🔴 Essential | 出入国在留管理庁・文化庁「在留支援のためのやさしい日本語ガイドライン」別冊書き換え例 | Term list | The closest thing to a national standard |
| 🔴 Essential | 出入国在留管理庁「やさしい日本語書き換えツール」 | Term list | Web-based vocabulary database; may need manual export |
| 🔴 Essential | 弘前大学「災害基礎語彙集成」（地震・大雨・洪水・土砂災害各100語） | Term list | Authoritative disaster vocabulary. Note: academic source, not government — included for coverage despite weakening the 前例主義 framing |
| 🟡 High | 鳥取県 防災ハンドブック（2023） | Sentence examples by scenario | Covers 地震/津波, 台風/大雨, 大雪, 避難所 |
| 🟡 High | 川崎市〈やさしい日本語〉ガイドライン 第2版（2023） | Term list + sentences | One of the more thorough municipal guides |
| 🟡 High | 札幌市 やさしい日本語ガイドライン（2025） | Term list + sentences | Includes spoken language guidance. Verify publication date. |
| 🟡 High | 福岡市「使ってみよう やさしい日本語」+ 用語集 | Term list | Separate 用語集 PDF is well-structured |
| 🟡 High | 三重県 やさしい日本語ガイドライン（2025） | Term list + sentences | Includes 言い換えリスト appendix. Verify publication date. |
| 🟢 Desirable | 静岡県「やさしい日本語の手引き」 | Sentences | Good before/after prose examples |
| 🟢 Desirable | 大阪市 防災やさしい日本語文例集 | Sentences | 地震 and 台風 scenarios |
| 🟢 Desirable | 宇都宮市 外国人市民への情報提供ガイドライン | Sentences | Broad 行政手続 coverage |

---

## 6. Lookup Interface

The system is implemented as a spreadsheet (Google Sheets or Excel). All user-facing headers and labels are in Japanese. Tabs are ordered by usage frequency — the primary search interface comes first.

### 6.1 Design principles
- **Japanese-first:** All column headers, labels, and instructions are in Japanese. No English in user-facing tabs.
- **Minimal columns:** User-facing tabs show only fields a non-technical staff member needs. Technical/internal fields (`entry_type`, `original_normalized`, `is_negative_example`, etc.) are kept only in the backing data tab.
- **`retain_original` handling:** Instead of showing a separate boolean column, entries where the source recommends retaining the original term are annotated inline in the 備考 (notes) column with `※原語を残す`.

### 6.2 Tab order

| # | Tab name | Purpose |
|---|----------|---------|
| 1 | `検索` | Primary search interface (staff use this most) |
| 2 | `合意状況` | Consensus view — how many organizations agree on each rendering |
| 3 | `データ` | Raw backing data with all fields (for maintenance/debugging) |

### `検索` tab (formerly `lookup`)
The staff-facing search interface:
- **Cell A1:** label `検索語を入力：`
- **Cell B1:** search input cell (highlighted)
- **Results area (row 5+):** FILTER formula that returns all rows from `データ` where 原文, やさしい日本語, or 備考 contains the search term
- **Columns shown:**

| Header | Source field | Description |
|--------|-------------|-------------|
| 原文 | `original` | Original Japanese |
| やさしい日本語 | `yasashii` | Easy Japanese rendering |
| 出典（組織） | `source_org` | Issuing organization |
| 出典（文書） | `source_document` | Document title |
| 備考 | `notes` + `retain_original` | Notes, with `※原語を残す` appended when `retain_original` is true |

- **Sort order:** by 出典（組織） alphabetically

### `合意状況` tab (formerly `consensus`)
A pre-computed pivot over `データ` grouped by normalized original term and やさしい日本語 rendering, counting distinct organizations. Shows at a glance how many organizations use each rendering for a given term. Only includes `entry_type = term`.

| Header | Description |
|--------|-------------|
| 原文 | Normalized original term |
| やさしい日本語 | Easy Japanese rendering |
| 組織数 | Number of distinct organizations using this rendering |
| 出典組織 | Comma-separated list of organizations |

### `データ` tab (formerly `data`)
The raw corpus with all fields from §5.1. This tab is for maintenance and data updates — staff do not need to use it directly. Auto-filter is enabled for ad-hoc exploration.

---

## 7. Non-Goals (out of scope for v1)

- Automated やさしい日本語 generation or AI rewriting
- Fuzzy or semantic sentence similarity search
- Management of the organization's own output documents
- Real-time web crawling for new government publications
- Multilingual display
- A web-based UI (deferred to a potential v2)

---

## 8. Open Questions

| # | Question | Why it matters |
|---|----------|----------------|
| OQ-1 | Who owns ongoing curation? Sources need to be checked for updates roughly annually. | Without an owner, the corpus goes stale. This should be assigned before launch, not left open. |

---

## 9. Success Criteria

The system is working if:

- A staff member can look up any common administrative or disaster-related term and see in under 60 seconds how other governments have handled it
- Disputed choices in internal review can be resolved by pointing to source documents rather than personal preference
- New staff can orient to やさしい日本語 norms by browsing existing examples rather than reading guidelines from scratch
