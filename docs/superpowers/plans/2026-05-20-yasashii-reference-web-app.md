# やさしい日本語 Reference Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Vite web app that compiles into one self-contained HTML file for read-only やさしい日本語 precedent lookup in modern Edge.

**Architecture:** Use a Vite + React + TypeScript frontend for the UI. A Node build-time script reads `data/*.json`, `data/sources.csv`, and `data/jlpt/*.csv`, precomputes compact evidence data, and writes `src/generated/app-data.ts`; Vite bundles the React app, `vite-plugin-singlefile` inlines JS/CSS into `dist/index.html`, and a postbuild script writes the final deliverable to `dist/yasashii-reference.html`.

**Tech Stack:** Vite, React, TypeScript, `@vitejs/plugin-react`, `vite-plugin-singlefile`, Node standard library, Node built-in test runner.

---

## File Structure

- Create `package.json`: npm scripts and dev dependencies.
- Create `tsconfig.json`: TypeScript config for Vite.
- Create `vite.config.ts`: Vite config with React, `base: "./"`, and `viteSingleFile()`.
- Create `index.html`: Vite HTML entry.
- Create `scripts/build-data.mjs`: Reads project data and generates `src/generated/app-data.ts`.
- Create `scripts/finalize-singlefile.mjs`: Copies `dist/index.html` to `dist/yasashii-reference.html` and checks for external asset references.
- Create `src/main.tsx`: React app entry point.
- Create `src/App.tsx`: App state, filtering, ranking, and component composition.
- Create `src/styles.css`: Evidence-first responsive styling.
- Create `src/types.ts`: Shared payload types.
- Create `src/generated/.gitkeep`: Keeps generated directory present; `app-data.ts` is generated.
- Create `tests/build-data.test.mjs`: Tests data normalization, source joins, consensus grouping, and generated output constraints.
- Create or update `WEB_APP.md`: Build/open/verify instructions.

This project is not currently a git repository, so commit steps are written as checkpoints.

---

### Task 1: Scaffold Vite Project Files

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `vite.config.ts`
- Create: `index.html`
- Create: `src/generated/.gitkeep`

- [ ] **Step 1: Create `package.json`**

```json
{
  "name": "yasashii-reference-web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "npm run data:build && vite",
    "data:build": "node scripts/build-data.mjs",
    "build": "npm run data:build && vite build && node scripts/finalize-singlefile.mjs",
    "test": "node --test tests/*.test.mjs",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  },
  "devDependencies": {
    "@types/react": "^19.2.0",
    "@types/react-dom": "^19.2.0",
    "@vitejs/plugin-react": "^5.1.0",
    "typescript": "^5.9.0",
    "vite": "^7.3.0",
    "vite-plugin-singlefile": "^2.3.0"
  }
}
```

- [ ] **Step 2: Create `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "jsx": "react-jsx",
    "moduleResolution": "Bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true
  },
  "include": ["src", "vite.config.ts"]
}
```

- [ ] **Step 3: Create `vite.config.ts`**

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  base: "./",
  plugins: [
    react(),
    viteSingleFile({
      removeViteModuleLoader: true
    })
  ],
  build: {
    target: "es2022",
    outDir: "dist",
    emptyOutDir: true
  }
});
```

- [ ] **Step 4: Create `index.html`**

```html
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>やさしい日本語 前例リファレンス</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Create generated directory marker**

Create `src/generated/.gitkeep` as an empty file.

- [ ] **Step 6: Install dependencies**

Run:

```bash
npm install
```

Expected: `node_modules/` and `package-lock.json` are created. If sandboxed network access fails, rerun with escalation because dependency download is required for the Vite build.

- [ ] **Step 7: Checkpoint**

Record that the Vite project scaffolding exists and dependencies install successfully.

---

### Task 2: Build Data Generation Script With Tests

**Files:**
- Create: `scripts/build-data.mjs`
- Create: `tests/build-data.test.mjs`

- [ ] **Step 1: Create failing tests**

Create `tests/build-data.test.mjs`:

```js
import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  buildPayload,
  loadEntries,
  loadJlptLevels,
  loadSources,
  normalizeYasashii,
  renderGeneratedModule,
  stripFurigana
} from "../scripts/build-data.mjs";

test("stripFurigana removes hiragana parentheticals only", () => {
  assert.equal(stripFurigana("避難（ひなん）する"), "避難する");
  assert.equal(stripFurigana("避難(ひなん)する"), "避難する");
  assert.equal(stripFurigana("雇用保険(No.41)"), "雇用保険(No.41)");
});

test("normalizeYasashii removes furigana and spaces", () => {
  assert.equal(normalizeYasashii("逃（に）げて ください"), "逃げてください");
  assert.equal(normalizeYasashii("危ない　ので"), "危ないので");
});

test("loadEntries joins source metadata and deduplicates", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "yasashii-data-"));
  await writeFile(
    path.join(dir, "sources.csv"),
    "source_id,source_org,source_document,source_url,source_date,source_category,source_description,source_short_name,source_vocab_standard,source_notes\n" +
      "01,川崎市,文書A,https://example.test/a.pdf,2023,行政,説明,川崎市GL,,注意\n",
    "utf8"
  );
  const entries = [{
    source_id: "01",
    source_org: "川崎市",
    source_document: "文書A",
    source_date: "2023",
    domain: "防災",
    entry_type: "term",
    original: "避難",
    original_normalized: "避難",
    yasashii: "逃（に）げる こと",
    notes: "",
    retain_original: false,
    is_negative_example: false
  }];
  await writeFile(path.join(dir, "01_sample.json"), JSON.stringify([...entries, ...entries]), "utf8");
  const loaded = await loadEntries(dir, await loadSources(dir));
  assert.equal(loaded.length, 1);
  assert.equal(loaded[0].yasashii, "逃げること");
  assert.equal(loaded[0].sourceShortName, "川崎市GL");
});

test("loadJlptLevels keeps easiest duplicate level", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "yasashii-jlpt-"));
  await mkdir(path.join(dir, "jlpt"));
  await writeFile(path.join(dir, "jlpt", "n2.csv"), "expression\n避難\n", "utf8");
  await writeFile(path.join(dir, "jlpt", "n4.csv"), "expression\n避難\n", "utf8");
  const levels = await loadJlptLevels(dir);
  assert.equal(levels.get("避難"), "N4");
});

test("buildPayload groups term consensus and keeps sentence evidence", () => {
  const payload = buildPayload([
    {
      sourceId: "01",
      sourceOrg: "川崎市",
      sourceDocument: "文書A",
      sourceDate: "2023",
      sourceShortName: "川崎市GL",
      sourceCategory: "行政",
      sourceUrl: "https://example.test/a.pdf",
      domains: ["防災"],
      entryType: "term",
      original: "避難",
      originalNormalized: "避難",
      yasashii: "逃げること",
      notes: "注1",
      retainOriginal: false,
      isNegativeExample: false
    },
    {
      sourceId: "02",
      sourceOrg: "鳥取県",
      sourceDocument: "文書B",
      sourceDate: "2024",
      sourceShortName: "鳥取県HB",
      sourceCategory: "行政",
      sourceUrl: "https://example.test/b.pdf",
      domains: ["防災"],
      entryType: "term",
      original: "避難（ひなん）",
      originalNormalized: "避難",
      yasashii: "逃げること",
      notes: "",
      retainOriginal: true,
      isNegativeExample: false
    },
    {
      sourceId: "01",
      sourceOrg: "川崎市",
      sourceDocument: "文書A",
      sourceDate: "2023",
      sourceShortName: "川崎市GL",
      sourceCategory: "行政",
      sourceUrl: "https://example.test/a.pdf",
      domains: ["防災"],
      entryType: "sentence",
      original: "避難してください",
      originalNormalized: "",
      yasashii: "逃げてください",
      notes: "",
      retainOriginal: false,
      isNegativeExample: false
    }
  ], new Map([["避難", "N3"]]));
  assert.equal(payload.terms[0].sourceCount, 2);
  assert.equal(payload.terms[0].retainOriginal, true);
  assert.equal(payload.sentences[0].sourceShortName, "川崎市GL");
  assert.deepEqual(payload.filters.domains, ["防災"]);
  assert.deepEqual(payload.filters.sourceCategories, ["行政"]);
});

test("renderGeneratedModule escapes script close tags", () => {
  const moduleText = renderGeneratedModule({
    meta: { termCount: 1, sentenceCount: 0, sourceCount: 1 },
    filters: { domains: [], sourceCategories: [] },
    terms: [{ original: "</script>", yasashii: "安全", sourceCount: 1 }],
    sentences: []
  });
  assert.match(moduleText, /<\\\/script>/);
  assert.match(moduleText, /export const appData/);
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
npm test
```

Expected: tests fail because `scripts/build-data.mjs` does not exist.

- [ ] **Step 3: Create `scripts/build-data.mjs`**

```js
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export function stripFurigana(text = "") {
  return String(text).replace(/（[ぁ-ゖー]+）/g, "").replace(/\([ぁ-ゖー]+\)/g, "");
}

export function normalizeYasashii(text = "") {
  return stripFurigana(text).replaceAll(" ", "").replaceAll("　", "");
}

function parseCsvLine(line) {
  const cells = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      cells.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  cells.push(current);
  return cells;
}

function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter((line) => line.length > 0);
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

function splitDomains(value = "") {
  return String(value).split(",").map((part) => part.trim()).filter(Boolean);
}

export async function loadSources(dataDir) {
  const rows = parseCsv(await readFile(path.join(dataDir, "sources.csv"), "utf8"));
  return new Map(rows.map((row) => [row.source_id, row]));
}

export async function loadEntries(dataDir, sources) {
  const files = (await readdir(dataDir)).filter((file) => /^\d+.*\.json$/.test(file)).sort();
  const entries = [];
  const seen = new Set();
  for (const file of files) {
    const sourceEntries = JSON.parse(await readFile(path.join(dataDir, file), "utf8"));
    for (const entry of sourceEntries) {
      const yasashii = normalizeYasashii(entry.yasashii ?? "");
      const key = [entry.source_id ?? "", entry.original ?? "", yasashii, entry.entry_type ?? ""].join("\u0000");
      if (seen.has(key)) continue;
      seen.add(key);
      const source = sources.get(entry.source_id) ?? {};
      entries.push({
        sourceId: entry.source_id ?? "",
        sourceOrg: entry.source_org ?? source.source_org ?? "",
        sourceDocument: entry.source_document ?? source.source_document ?? "",
        sourceDate: entry.source_date ?? source.source_date ?? "",
        sourceShortName: source.source_short_name ?? "",
        sourceCategory: source.source_category ?? "",
        sourceUrl: source.source_url ?? "",
        domains: splitDomains(entry.domain ?? ""),
        entryType: entry.entry_type ?? "",
        original: entry.original ?? "",
        originalNormalized: entry.original_normalized ?? "",
        yasashii,
        notes: entry.notes ?? "",
        retainOriginal: Boolean(entry.retain_original),
        isNegativeExample: Boolean(entry.is_negative_example)
      });
    }
  }
  return entries;
}

function easierLevel(a, b) {
  return Number(a.slice(1)) > Number(b.slice(1)) ? a : b;
}

function addJlpt(levels, expression, level) {
  const key = String(expression ?? "").trim();
  const value = String(level ?? "").trim();
  if (!key || !/^N[1-5]$/.test(value)) return;
  levels.set(key, levels.has(key) ? easierLevel(levels.get(key), value) : value);
}

export async function loadJlptLevels(dataDir) {
  const levels = new Map();
  const jlptDir = path.join(dataDir, "jlpt");
  for (let n = 1; n <= 5; n += 1) {
    try {
      const rows = parseCsv(await readFile(path.join(jlptDir, `n${n}.csv`), "utf8"));
      rows.forEach((row) => addJlpt(levels, row.expression, `N${n}`));
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  return levels;
}

function sourceSummary(entry) {
  return {
    sourceId: entry.sourceId,
    sourceOrg: entry.sourceOrg,
    sourceDocument: entry.sourceDocument,
    sourceDate: entry.sourceDate,
    sourceShortName: entry.sourceShortName,
    sourceCategory: entry.sourceCategory,
    sourceUrl: entry.sourceUrl,
    domains: entry.domains,
    notes: entry.notes,
    retainOriginal: entry.retainOriginal,
    isNegativeExample: entry.isNegativeExample
  };
}

export function buildPayload(entries, jlptLevels) {
  const groups = new Map();
  for (const entry of entries.filter((item) => item.entryType === "term")) {
    const original = entry.originalNormalized || stripFurigana(entry.original);
    const key = `${original}\u0000${entry.yasashii}`;
    if (!groups.has(key)) {
      groups.set(key, {
        original,
        yasashii: entry.yasashii,
        sourceOrgs: new Set(),
        sourceShortNames: new Set(),
        sourceCategories: new Set(),
        domains: new Set(),
        notes: new Set(),
        retainOriginal: false,
        isNegativeExample: false,
        sources: [],
        jlpt: jlptLevels.get(original) ?? ""
      });
    }
    const group = groups.get(key);
    if (entry.sourceOrg) group.sourceOrgs.add(entry.sourceOrg);
    if (entry.sourceShortName) group.sourceShortNames.add(entry.sourceShortName);
    if (entry.sourceCategory) group.sourceCategories.add(entry.sourceCategory);
    entry.domains.forEach((domain) => group.domains.add(domain));
    if (entry.notes) group.notes.add(entry.notes);
    group.retainOriginal ||= entry.retainOriginal;
    group.isNegativeExample ||= entry.isNegativeExample;
    group.sources.push(sourceSummary(entry));
  }

  const terms = [...groups.values()].map((group) => ({
    original: group.original,
    yasashii: group.yasashii,
    sourceCount: group.sourceOrgs.size,
    sourceOrgs: [...group.sourceOrgs].sort(),
    sourceShortNames: [...group.sourceShortNames].sort(),
    sourceCategories: [...group.sourceCategories].sort(),
    domains: [...group.domains].sort(),
    notes: [...group.notes].sort().slice(0, 5),
    retainOriginal: group.retainOriginal,
    isNegativeExample: group.isNegativeExample,
    sources: group.sources,
    jlpt: group.jlpt,
    searchText: [
      group.original,
      group.yasashii,
      ...group.notes,
      ...group.sourceOrgs,
      ...group.sourceShortNames,
      ...group.sourceCategories,
      ...group.domains
    ].join(" ").toLowerCase()
  })).sort((a, b) => b.sourceCount - a.sourceCount || a.original.localeCompare(b.original, "ja"));

  const sentences = entries.filter((entry) => entry.entryType === "sentence").map((entry) => ({
    ...sourceSummary(entry),
    original: entry.original,
    yasashii: entry.yasashii,
    searchText: [
      entry.original,
      entry.yasashii,
      entry.notes,
      entry.sourceOrg,
      entry.sourceDocument,
      entry.sourceShortName,
      ...entry.domains
    ].join(" ").toLowerCase()
  }));

  return {
    meta: {
      termCount: terms.length,
      sentenceCount: sentences.length,
      sourceCount: new Set(entries.map((entry) => entry.sourceId).filter(Boolean)).size
    },
    filters: {
      domains: [...new Set(entries.flatMap((entry) => entry.domains))].sort(),
      sourceCategories: [...new Set(entries.map((entry) => entry.sourceCategory).filter(Boolean))].sort()
    },
    terms,
    sentences
  };
}

export function renderGeneratedModule(payload) {
  const json = JSON.stringify(payload, null, 0).replaceAll("</", "<\\/");
  return `import type { AppPayload } from "../types";\n\nexport const appData = ${json} satisfies AppPayload;\n`;
}

export async function buildData({ dataDir = path.join(rootDir, "data"), output = path.join(rootDir, "src/generated/app-data.ts") } = {}) {
  const sources = await loadSources(dataDir);
  const entries = await loadEntries(dataDir, sources);
  const jlptLevels = await loadJlptLevels(dataDir);
  const payload = buildPayload(entries, jlptLevels);
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, renderGeneratedModule(payload), "utf8");
  return payload;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const payload = await buildData();
  console.log(`Generated app data: ${payload.meta.termCount} terms, ${payload.meta.sentenceCount} sentences`);
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
npm test
```

Expected: PASS.

- [ ] **Step 5: Generate app data**

Run:

```bash
npm run data:build
```

Expected: `src/generated/app-data.ts` exists and contains `export const appData`.

- [ ] **Step 6: Checkpoint**

Record that data generation is tested and the app data module is generated from the real corpus.

---

### Task 3: Implement App Types, Styling, And Rendering

**Files:**
- Create: `src/types.ts`
- Create: `src/styles.css`
- Create: `src/App.tsx`
- Create: `src/main.tsx`

- [ ] **Step 1: Create `src/types.ts`**

```ts
export interface SourceSummary {
  sourceId: string;
  sourceOrg: string;
  sourceDocument: string;
  sourceDate: string;
  sourceShortName: string;
  sourceCategory: string;
  sourceUrl: string;
  domains: string[];
  notes: string;
  retainOriginal: boolean;
  isNegativeExample: boolean;
}

export interface TermEvidence {
  original: string;
  yasashii: string;
  sourceCount: number;
  sourceOrgs: string[];
  sourceShortNames: string[];
  sourceCategories: string[];
  domains: string[];
  notes: string[];
  retainOriginal: boolean;
  isNegativeExample: boolean;
  sources: SourceSummary[];
  jlpt: string;
  searchText: string;
}

export interface SentenceEvidence extends SourceSummary {
  original: string;
  yasashii: string;
  searchText: string;
}

export interface AppPayload {
  meta: {
    termCount: number;
    sentenceCount: number;
    sourceCount: number;
  };
  filters: {
    domains: string[];
    sourceCategories: string[];
  };
  terms: TermEvidence[];
  sentences: SentenceEvidence[];
}
```

- [ ] **Step 2: Create `src/styles.css`**

Use this styling baseline:

```css
:root {
  color-scheme: light;
  font-family: "Yu Gothic", "Meiryo", system-ui, sans-serif;
  --ink: #172126;
  --muted: #607078;
  --line: #d8e0e3;
  --soft: #f5f7f7;
  --paper: #ffffff;
  --field: #fffdf5;
  --accent: #2f6f5e;
  --accent-soft: #e5f0ec;
  --warn: #8b5e00;
  --warn-soft: #fff6dd;
  --bad: #8f2d25;
  --bad-soft: #ffe8e5;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  color: var(--ink);
  background: #eef2f1;
}

button,
input,
select {
  font: inherit;
}

.app {
  width: min(1280px, 100%);
  margin: 0 auto;
  padding: 28px;
}

.title {
  margin: 0 0 6px;
  font-size: 28px;
  letter-spacing: 0;
}

.subtitle {
  margin: 0 0 18px;
  color: var(--muted);
  line-height: 1.7;
}

.search-panel,
.card,
.sentence-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.search-panel {
  padding: 18px;
}

.search-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
}

.query {
  width: 100%;
  border: 2px solid #9cb5ad;
  border-radius: 6px;
  background: var(--field);
  padding: 12px 14px;
  font-size: 20px;
}

.query:focus {
  border-color: var(--accent);
  outline: 3px solid var(--accent-soft);
}

.button {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--paper);
  color: var(--ink);
  padding: 8px 12px;
  cursor: pointer;
}

.filters,
.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
}

.filters {
  margin-top: 10px;
}

.filter {
  max-width: 220px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--soft);
  padding: 7px 10px;
}

.summary {
  margin-top: 12px;
  border-top: 1px solid var(--line);
  padding-top: 12px;
  color: var(--muted);
  font-size: 13px;
}

.summary strong {
  color: var(--ink);
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.75fr);
  gap: 18px;
  margin-top: 18px;
  align-items: start;
}

.section-title {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 15px;
}

.card,
.sentence-card {
  margin-bottom: 10px;
  padding: 14px;
}

.term-grid {
  display: grid;
  grid-template-columns: 170px 1fr;
  gap: 16px;
}

.label {
  margin-bottom: 4px;
  color: var(--muted);
  font-size: 12px;
}

.original {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.5;
}

.yasashii {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.55;
}

.sentence-text {
  line-height: 1.65;
}

.meta {
  margin-top: 10px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.8;
}

.chip {
  display: inline-block;
  margin: 0 4px 4px 0;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--soft);
  padding: 2px 7px;
  white-space: nowrap;
}

.chip.warn {
  color: var(--warn);
  background: var(--warn-soft);
  border-color: #ead28c;
}

.chip.bad {
  color: var(--bad);
  background: var(--bad-soft);
  border-color: #efb5ad;
}

.empty {
  border: 1px dashed var(--line);
  border-radius: 8px;
  background: var(--paper);
  padding: 28px;
  color: var(--muted);
  line-height: 1.8;
}

a {
  color: #075b9a;
}

@media (max-width: 900px) {
  .app {
    padding: 16px;
  }

  .layout,
  .term-grid,
  .search-row {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 3: Create `src/App.tsx`**

```tsx
import { useMemo, useState } from "react";
import { appData } from "./generated/app-data";
import type { SentenceEvidence, TermEvidence } from "./types";

type EntryTypeFilter = "all" | "term" | "sentence";

interface ResultSet {
  terms: TermEvidence[];
  sentences: SentenceEvidence[];
}

function scoreTerm(term: TermEvidence, query: string): number {
  if (!query) return term.sourceCount;
  if (term.original === query) return 1000 + term.sourceCount;
  if (term.original.startsWith(query)) return 800 + term.sourceCount;
  if (term.yasashii.includes(query)) return 650 + term.sourceCount;
  if (term.searchText.includes(query)) return 400 + term.sourceCount;
  return 0;
}

function domainOk(item: { domains: string[] }, domain: string): boolean {
  return !domain || item.domains.includes(domain);
}

function categoryOk(item: TermEvidence | SentenceEvidence, category: string): boolean {
  if (!category) return true;
  if ("sourceCategories" in item) return item.sourceCategories.includes(category);
  return item.sourceCategory === category;
}

function conversionLabel(sentence: SentenceEvidence, query: string): string {
  if (!query || !sentence.original.includes(query)) return "";
  return sentence.yasashii.includes(query) ? "そのまま" : "やさしくされた";
}

function Chip({ label, tone = "" }: { label: string; tone?: "warn" | "bad" | "" }) {
  if (!label) return null;
  return <span className={`chip ${tone}`}>{label}</span>;
}

function Summary({ terms, sentences }: ResultSet) {
  const sourceOrgs = new Set<string>();
  terms.forEach((term) => term.sourceOrgs.forEach((org) => sourceOrgs.add(org)));
  sentences.forEach((sentence) => {
    if (sentence.sourceOrg) sourceOrgs.add(sentence.sourceOrg);
  });

  return (
    <div className="summary" aria-label="検索サマリー">
      <span><strong>用語前例</strong> {terms.length}件</span>
      <span><strong>文例</strong> {sentences.length}件</span>
      <span><strong>出典組織</strong> {sourceOrgs.size}組織</span>
      <span><strong>原語保持</strong> {terms.some((term) => term.retainOriginal) ? "あり" : "なし"}</span>
    </div>
  );
}

function TermCard({ term }: { term: TermEvidence }) {
  return (
    <article className="card">
      <div className="term-grid">
        <div>
          <div className="label">原文</div>
          <div className="original">{term.original}</div>
        </div>
        <div>
          <div className="label">やさしい日本語の前例</div>
          <div className="yasashii">{term.yasashii}</div>
          <div className="meta">
            {term.sourceCategories.map((category) => <Chip key={category} label={category} />)}
            {term.retainOriginal ? <Chip label="原語を残す" tone="warn" /> : null}
            {term.isNegativeExample ? <Chip label="非推奨例" tone="bad" /> : null}
            <span>出典 {term.sourceCount}: {term.sourceShortNames.join("、")}</span>
            {term.notes.length ? <><br /><span>備考: {term.notes.join("；")}</span></> : null}
          </div>
        </div>
      </div>
    </article>
  );
}

function SentenceCard({ sentence, query }: { sentence: SentenceEvidence; query: string }) {
  const label = conversionLabel(sentence, query);
  return (
    <article className="sentence-card">
      <div className="label">原文</div>
      <div className="sentence-text">{sentence.original}</div>
      <div className="label">やさしい日本語</div>
      <div className="sentence-text">{sentence.yasashii}</div>
      <div className="meta">
        {label ? <Chip label={label} tone={label === "やさしくされた" ? "warn" : ""} /> : null}
        <span>{sentence.sourceShortName || sentence.sourceOrg}</span>
        {sentence.isNegativeExample ? <Chip label="非推奨例" tone="bad" /> : null}
        {sentence.sourceUrl ? <> <a href={sentence.sourceUrl}>出典</a></> : null}
      </div>
    </article>
  );
}

export function App() {
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");
  const [category, setCategory] = useState("");
  const [type, setType] = useState<EntryTypeFilter>("all");
  const [termLimit, setTermLimit] = useState(12);
  const [sentenceLimit, setSentenceLimit] = useState(12);

  const normalizedQuery = query.trim().toLowerCase();

  const results = useMemo<ResultSet>(() => {
    const terms = type === "sentence" ? [] : appData.terms
      .map((term) => ({ term, score: scoreTerm(term, normalizedQuery) }))
      .filter(({ term, score }) => (!normalizedQuery || score > 0) && domainOk(term, domain) && categoryOk(term, category))
      .sort((a, b) => b.score - a.score || b.term.sourceCount - a.term.sourceCount)
      .map(({ term }) => term);

    const sentences = type === "term" ? [] : appData.sentences
      .filter((sentence) => (!normalizedQuery || sentence.searchText.includes(normalizedQuery)) && domainOk(sentence, domain) && categoryOk(sentence, category));

    return { terms, sentences };
  }, [category, domain, normalizedQuery, type]);

  function resetLimits() {
    setTermLimit(12);
    setSentenceLimit(12);
  }

  const hasSearchContext = Boolean(normalizedQuery || domain || category);
  const visibleTerms = results.terms.slice(0, termLimit);
  const visibleSentences = results.sentences.slice(0, sentenceLimit);

  return (
    <div className="app">
      <header>
        <h1 className="title">やさしい日本語 前例リファレンス</h1>
        <p className="subtitle">公的資料にある書き換え例を検索し、前例にもとづいて判断するための参照ツールです。</p>
      </header>
      <main>
        <section className="search-panel" aria-label="検索">
          <div className="search-row">
            <input
              className="query"
              type="search"
              autoComplete="off"
              placeholder="調べたい語を入力（例：避難、届出、津波）"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                resetLimits();
              }}
            />
            <button
              className="button"
              type="button"
              onClick={() => {
                setQuery("");
                resetLimits();
              }}
            >
              クリア
            </button>
          </div>
          <div className="filters">
            <select className="filter" aria-label="分野" value={domain} onChange={(event) => { setDomain(event.target.value); resetLimits(); }}>
              <option value="">すべての分野</option>
              {appData.filters.domains.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <select className="filter" aria-label="出典種別" value={category} onChange={(event) => { setCategory(event.target.value); resetLimits(); }}>
              <option value="">すべての出典種別</option>
              {appData.filters.sourceCategories.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <select className="filter" aria-label="種別" value={type} onChange={(event) => { setType(event.target.value as EntryTypeFilter); resetLimits(); }}>
              <option value="all">用語と文例</option>
              <option value="term">用語のみ</option>
              <option value="sentence">文例のみ</option>
            </select>
          </div>
          <Summary terms={results.terms} sentences={results.sentences} />
        </section>

        <section className="layout">
          <div>
            <h2 className="section-title">用語前例</h2>
            {!hasSearchContext ? (
              <div className="empty">検索語を入力してください。例: 避難、避難指示、届出、津波</div>
            ) : visibleTerms.length ? (
              <>
                {visibleTerms.map((term) => <TermCard key={`${term.original}-${term.yasashii}`} term={term} />)}
                {results.terms.length > visibleTerms.length ? <button className="button" type="button" onClick={() => setTermLimit(termLimit + 12)}>もっと見る</button> : null}
              </>
            ) : (
              <div className="empty">用語前例は見つかりませんでした。</div>
            )}
          </div>
          <aside>
            <h2 className="section-title">文例</h2>
            {!hasSearchContext ? (
              <div className="empty">文例もここに表示されます。</div>
            ) : visibleSentences.length ? (
              <>
                {visibleSentences.map((sentence, index) => <SentenceCard key={`${sentence.sourceId}-${index}`} sentence={sentence} query={normalizedQuery} />)}
                {results.sentences.length > visibleSentences.length ? <button className="button" type="button" onClick={() => setSentenceLimit(sentenceLimit + 12)}>もっと見る</button> : null}
              </>
            ) : (
              <div className="empty">文例は見つかりませんでした。</div>
            )}
          </aside>
        </section>
      </main>
    </div>
  );
}
```

- [ ] **Step 4: Create `src/main.tsx`**

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

const root = document.getElementById("app");

if (!root) {
  throw new Error("Missing #app root");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 5: Run typecheck**

Run:

```bash
npm run data:build
npm run typecheck
```

Expected: TypeScript passes.

- [ ] **Step 6: Checkpoint**

Record that the React Vite app renders the evidence console from generated data.

---

### Task 4: Finalize Single HTML Build

**Files:**
- Create: `scripts/finalize-singlefile.mjs`
- Generated: `dist/index.html`
- Generated: `dist/yasashii-reference.html`

- [ ] **Step 1: Create `scripts/finalize-singlefile.mjs`**

```js
import { copyFile, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const builtHtml = path.join(rootDir, "dist", "index.html");
const finalHtml = path.join(rootDir, "dist", "yasashii-reference.html");

const html = await readFile(builtHtml, "utf8");
const forbidden = [
  /<script\b[^>]*\bsrc=/i,
  /<link\b[^>]*rel=["']stylesheet["']/i,
  /fetch\s*\(/,
  /https:\/\/cdn/i,
  /http:\/\/fonts|https:\/\/fonts/i
];

const failed = forbidden.find((pattern) => pattern.test(html));
if (failed) {
  throw new Error(`Single-file verification failed: ${failed}`);
}

await copyFile(builtHtml, finalHtml);
console.log(`Wrote ${path.relative(rootDir, finalHtml)}`);
```

- [ ] **Step 2: Run production build**

Run:

```bash
npm run build
```

Expected:

- `dist/index.html` exists
- `dist/yasashii-reference.html` exists
- The build prints `Wrote dist/yasashii-reference.html`
- No `assets/` references are required by the final HTML

- [ ] **Step 3: Inspect generated HTML for external dependencies**

Run:

```bash
node -e "const fs=require('fs'); const html=fs.readFileSync('dist/yasashii-reference.html','utf8'); console.log(JSON.stringify({bytes:Buffer.byteLength(html), scriptSrc:/<script\\b[^>]*\\bsrc=/i.test(html), stylesheet:/<link\\b[^>]*rel=[\"']stylesheet[\"']/i.test(html), fetch:html.includes('fetch(')}, null, 2));"
```

Expected:

```json
{
  "scriptSrc": false,
  "stylesheet": false,
  "fetch": false
}
```

The exact byte count may vary.

- [ ] **Step 4: Checkpoint**

Record that the Vite build creates a single self-contained deliverable.

---

### Task 5: Browser And Data Verification

**Files:**
- Modify: `tests/build-data.test.mjs`
- Generated: `dist/yasashii-reference.html`

- [ ] **Step 1: Add real data scale test**

Append to `tests/build-data.test.mjs`:

```js
test("real project data has expected scale and representative terms", async () => {
  const dataDir = path.resolve("data");
  const entries = await loadEntries(dataDir, await loadSources(dataDir));
  const payload = buildPayload(entries, await loadJlptLevels(dataDir));
  assert.ok(payload.meta.termCount > 1000, `termCount was ${payload.meta.termCount}`);
  assert.ok(payload.meta.sentenceCount > 10000, `sentenceCount was ${payload.meta.sentenceCount}`);
  const searchable = [
    ...payload.terms.slice(0, 5000).map((term) => `${term.original} ${term.yasashii}`),
    ...payload.sentences.slice(0, 5000).map((sentence) => `${sentence.original} ${sentence.yasashii}`)
  ].join("\n");
  assert.match(searchable, /避難/);
});
```

- [ ] **Step 2: Run tests, typecheck, and build**

Run:

```bash
npm test
npm run typecheck
npm run build
```

Expected: all commands pass.

- [ ] **Step 3: Run direct `file://` smoke test with Playwright if available**

Run:

```bash
node -e "const { chromium } = require('@playwright/test'); const path = require('path'); (async () => { const browser = await chromium.launch({ headless: true }); const page = await browser.newPage({ viewport: { width: 1280, height: 900 } }); const errors = []; page.on('pageerror', e => errors.push(e.message)); page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); }); await page.goto('file://' + path.resolve('dist/yasashii-reference.html'), { waitUntil: 'domcontentloaded' }); await page.locator('#query').fill('避難'); await page.waitForTimeout(300); const termText = await page.locator('#termResults').innerText(); const sentenceText = await page.locator('#sentenceResults').innerText(); console.log(JSON.stringify({ title: await page.title(), hasTermResults: !termText.includes('見つかりません'), hasSentenceResults: !sentenceText.includes('見つかりません'), errors }, null, 2)); await browser.close(); })().catch(err => { console.error(err); process.exit(1); });"
```

Expected:

```json
{
  "title": "やさしい日本語 前例リファレンス",
  "hasTermResults": true,
  "hasSentenceResults": true,
  "errors": []
}
```

If Playwright is unavailable in local dependencies, skip only this automation step and do the manual Edge checks.

- [ ] **Step 4: Manual Edge checks**

Open `dist/yasashii-reference.html` directly in modern Edge and test:

- `避難`
- `避難指示`
- `届出`
- `津波`
- `川崎市`
- A no-results query such as `zzzzzz`
- `分野` filter
- `出典種別` filter
- `用語のみ`
- `文例のみ`

Expected:

- The page opens without a server.
- No network access is required.
- Counts stay compact.
- The actual precedent wording is visually dominant.
- Source category chips remain secondary.
- No-result state is clear.

- [ ] **Step 5: Checkpoint**

Record commands run, browser check results, and any skipped automation.

---

### Task 6: Documentation And Handoff

**Files:**
- Create: `WEB_APP.md`
- Generated: `dist/yasashii-reference.html`

- [ ] **Step 1: Create `WEB_APP.md`**

```markdown
# やさしい日本語 前例リファレンス Web App

## What This Builds

This is a Vite + React app that builds into one self-contained HTML file:

```text
dist/yasashii-reference.html
```

The final HTML can be opened directly in modern Microsoft Edge. It does not require a server, network access, external assets, or installation on the viewing machine.

## Development

Install dependencies:

```bash
npm install
```

Run the dev server:

```bash
npm run dev
```

The dev server is only for development. It is not needed for deployment.

## Build

```bash
npm run build
```

The build process:

1. Reads `data/*.json`, `data/sources.csv`, and `data/jlpt/*.csv`
2. Generates `src/generated/app-data.ts`
3. Runs Vite
4. Inlines JavaScript and CSS into one HTML file
5. Writes `dist/yasashii-reference.html`

## Verify

```bash
npm test
npm run typecheck
npm run build
```

Then open `dist/yasashii-reference.html` directly in Edge and test:

- `避難`
- `避難指示`
- `届出`
- `津波`
- `川崎市`

## Data Maintenance

When adding a new JSON source under `data/`, also add the matching row to `data/sources.csv`.
```

- [ ] **Step 2: Run final verification**

Run:

```bash
npm test
npm run typecheck
npm run build
```

Expected: all pass.

- [ ] **Step 3: Final handoff summary**

Report:

- Created Vite + React source files
- Generated HTML path
- Test/typecheck/build results
- Browser verification results
- Any skipped automation
- Reminder that this directory is not a git repository, so no commit was made

---

## Self-Review Checklist

- Spec coverage: The plan now uses a Vite + React source app and builds a single self-contained HTML artifact, while preserving the evidence-only UI, quiet filters, compact counts, source metadata, and direct-file deployment constraints.
- Placeholder scan: This plan contains no unfinished placeholder markers or unspecified broad edge-case tasks.
- Type consistency: The plan uses `sourceShortName`, `sourceCategories`, `retainOriginal`, `isNegativeExample`, `terms`, and `sentences` consistently across build data, TypeScript types, and rendering.
