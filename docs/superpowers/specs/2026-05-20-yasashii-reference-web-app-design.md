# やさしい日本語 前例リファレンス Web App Design

Date: 2026-05-20

## Goal

Build a read-only, self-contained HTML web app that helps municipal staff inspect precedent evidence for converting Japanese into やさしい日本語.

The app should not recommend a final wording. It should make the available evidence legible enough that staff can decide how to write or review a phrase based on prior official examples.

## Deployment Constraint

The deliverable is a single HTML file that can be opened directly in modern Microsoft Edge.

The app must not require:

- A local or remote server
- Network access
- `fetch()` loading external JSON files
- External CDNs, fonts, or assets
- Installation steps on the user machine

## Source Data

The build process reads the existing project data:

- `data/*.json` for corpus entries
- `data/sources.csv` for source metadata
- `data/jlpt/*.csv` for JLPT vocabulary difficulty lookup

The app uses the existing corpus fields, including:

- `source_id`
- `source_org`
- `source_document`
- `source_date`
- `domain`
- `entry_type`
- `original`
- `original_normalized`
- `yasashii`
- `notes`
- `retain_original`
- `is_negative_example`

Source metadata from `sources.csv` is joined by `source_id`. Source category and short-name labels are displayed as low-emphasis metadata.

## App Shape

The app is a web-native evidence console, not a copy of the Excel tabs.

The main screen has:

- A prominent search input
- Quiet optional filters for `分野`, `出典種別`, and `用語/文例`
- A compact evidence strip showing context counts
- Term precedent cards as the primary result area
- Sentence examples as supporting evidence
- Source labels and links as secondary metadata

The selected layout is the "Search Console" direction: one focused search surface with evidence grouped around the user query.

## Visual Hierarchy

The most prominent information should be the actual precedent evidence:

1. The searched term or phrase and matching original text
2. Attested やさしい日本語 renderings
3. Sentence-level before/after examples
4. Evidence counts and organization spread
5. Source names, categories, dates, and links

Counts should not appear as large dashboard KPI cards. They should be a compact context strip under the search input:

- `用語前例`
- `文例`
- `出典組織`
- `原語保持`

Source type labels, such as national guidance, municipal source, or academic source, should be visible but visually quiet.

## Search Behavior

Search is evidence-oriented and broader than the Excel formula search.

The query is matched against:

- `original`
- `original_normalized`
- `yasashii`
- `notes`
- `domain`
- `source_org`
- `source_document`
- `source_short_name`

The first version uses deterministic client-side search, not semantic embeddings or AI rewriting.

Results should prioritize:

1. Exact matches on `original_normalized` or `original`
2. Prefix and substring term matches
3. Consensus term entries
4. Sentence examples containing the query
5. Source/document metadata matches

Empty search shows a calm starting state with example queries. No-result search shows a clear message and keeps filters visible so users can recover.

## Evidence Model

The build script precomputes term consensus rows from `entry_type = "term"` entries.

Consensus grouping key:

- `original_normalized`
- `yasashii`

For each group, compute:

- Distinct source organization count
- Source short-name list
- Source category labels
- Combined notes
- Whether any entry has `retain_original = true`

Sentence evidence uses `entry_type = "sentence"` entries.

For sentence evidence, compute whether the searched phrase was:

- `そのまま`: the query appears in both the original and the やさしい日本語 text
- `やさしくされた`: the query appears in the original but not in the やさしい日本語 text

This classification is displayed as evidence, not as a recommendation.

## Evidence-Only Stance

The app must not produce wording recommendations such as:

- `おすすめ`
- `言い換えたほうがよさそう`
- `この表現を使ってください`

It may display factual evidence such as:

- Number of source organizations
- Matching official examples
- Whether a source marks the original term as retained
- Whether sentence examples leave a term as-is or rewrite it
- Source categories and documents

## Interface Details

### Search Header

The top area contains:

- App title
- Brief subtitle explaining that the tool searches official precedent examples
- Search input
- Optional filters

Filters should be available without dominating the page. They can be compact chips, selects, or a collapsible filter row.

### Evidence Strip

The evidence strip is a single compact row under the search input.

It summarizes:

- Term precedent count
- Sentence example count
- Distinct source organization count
- Retain-original evidence presence

### Term Precedent Cards

Each card shows:

- `原文`
- `やさしい日本語の前例`
- Source count
- Source short names
- Notes, including `※原語を残す` when applicable
- Low-emphasis source category labels

Cards should be scannable and not table-like.

### Sentence Evidence

Sentence examples show:

- Original sentence
- やさしい日本語 sentence
- Source short name
- `そのまま` or `やさしくされた`

Sentence examples can appear in a right column on desktop and below term cards on narrower screens.

### Source Details

Source details remain secondary. They should be available through compact metadata or expandable detail, including:

- Organization
- Document
- Short name
- Source category
- Publication year
- URL link when available

## Data Packaging And Build System

The implementation should be a Vite + React web app that builds into one self-contained HTML file.

The source app can use normal frontend project structure during development, including React components, separate TypeScript, CSS, and build-time scripts. The production artifact must still be one HTML file.

Use Vite with React and a single-file build plugin, such as `vite-plugin-singlefile`, to inline JavaScript and CSS into the generated HTML. Configure Vite for file deployment with relative base paths.

A build-time data script should read the project data and generate an app data module before the Vite build runs.

Recommended output:

- `dist/yasashii-reference.html`

The generated HTML must embed:

- Precomputed app data as a JavaScript object or compressed JSON string
- All JavaScript logic
- All CSS

The generated file should not depend on project-relative paths once built.

Development dependencies are acceptable in the repository. Runtime dependencies are not acceptable in the final delivered HTML file.

## Performance

The corpus has roughly 20,000+ entries. Modern Edge can handle this in a single HTML file if the app:

- Precomputes consensus data during build
- Stores only the fields needed for lookup UI
- Debounces search input
- Limits initially rendered results
- Provides "show more" controls for long result sets

The first version should favor simple deterministic search over heavy indexing unless profiling shows a problem.

## Accessibility And Language

The user-facing interface is Japanese-first.

The app should:

- Use clear Japanese labels
- Avoid English in normal UI copy
- Support keyboard input and navigation
- Keep contrast high enough for office use
- Use semantic buttons and form controls
- Avoid tiny text for primary evidence

## Error And Edge States

The app handles:

- Empty query
- No results
- Filters that remove all results
- Missing source URL
- Missing source metadata
- Entries with empty notes
- Entries marked `is_negative_example`

Negative examples should be visibly labeled so users do not mistake them for recommended precedent.

## Verification

The generated HTML should be tested by opening it directly via `file://` in a Chromium/Edge-compatible browser.

Representative search cases:

- `避難`
- `避難指示`
- `届出`
- `津波`
- A source name such as `川崎市`
- A term with retain-original evidence
- A query with no results

Verification should check:

- The file opens without a server
- No network requests are required
- Search returns term and sentence evidence
- Filters work
- "Show more" works
- Source links display correctly
- Empty and no-result states are clear
- Primary evidence remains visually dominant over counts and source labels

## Out Of Scope For V1

- Admin editing UI
- AI rewriting
- Semantic similarity search
- Authentication
- Server-backed APIs
- Real-time corpus updates
- Multi-file deployment
- Excel-style sheet tabs
