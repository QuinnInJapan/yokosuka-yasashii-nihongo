import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function cleanText(text = "") {
  return String(text ?? "").replace(/[ \t\r\n\f\v\u00a0\u3000]+/g, " ").trim();
}

export function stripFurigana(text = "") {
  return cleanText(text).replace(/（[ぁ-ゖー]+）/g, "").replace(/\([ぁ-ゖー]+\)/g, "");
}

export function normalizeYasashii(text = "") {
  return stripFurigana(text).replace(/[ \t\r\n\f\v\u00a0\u3000]+/g, "");
}

function parseCsvLine(line) {
  const cells = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === "\"" && line[index + 1] === "\"") {
      current += "\"";
      index += 1;
    } else if (char === "\"") {
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
  return String(value).split(",").map((part) => cleanText(part)).filter(Boolean);
}

export async function loadSources(dataDir) {
  const rows = parseCsv(await readFile(path.join(dataDir, "sources.csv"), "utf8"));
  const cleanRows = rows.map((row) => Object.fromEntries(
    Object.entries(row).map(([key, value]) => [key, cleanText(value)]),
  ));
  return new Map(cleanRows.map((row) => [row.source_id, row]));
}

export async function loadEntries(dataDir, sources) {
  const files = (await readdir(dataDir)).filter((file) => /^\d+.*\.json$/.test(file)).sort();
  const entries = [];
  const seen = new Set();
  for (const file of files) {
    const sourceEntries = JSON.parse(await readFile(path.join(dataDir, file), "utf8"));
    for (const entry of sourceEntries) {
      const sourceId = cleanText(entry.source_id ?? "");
      const original = cleanText(entry.original ?? "");
      const originalNormalized = cleanText(entry.original_normalized ?? "");
      const yasashii = normalizeYasashii(entry.yasashii ?? "");
      const entryType = cleanText(entry.entry_type ?? "");
      const key = [sourceId, original, yasashii, entryType].join("\u0000");
      if (seen.has(key)) continue;
      seen.add(key);
      const source = sources.get(sourceId) ?? {};
      entries.push({
        sourceId,
        sourceOrg: cleanText(entry.source_org ?? source.source_org ?? ""),
        sourceDocument: cleanText(entry.source_document ?? source.source_document ?? ""),
        sourceDate: cleanText(entry.source_date ?? source.source_date ?? ""),
        sourceShortName: cleanText(source.source_short_name ?? ""),
        sourceCategory: cleanText(source.source_category ?? ""),
        sourceUrl: cleanText(source.source_url ?? ""),
        domains: splitDomains(entry.domain ?? ""),
        entryType,
        original,
        originalNormalized,
        yasashii,
        notes: cleanText(entry.notes ?? ""),
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

async function readCsvIfExists(filePath) {
  try {
    return parseCsv(await readFile(filePath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
}

export async function loadJlptLevels(dataDir) {
  const levels = new Map();
  const jlptDir = path.join(dataDir, "jlpt");
  for (let n = 1; n <= 5; n += 1) {
    const rows = await readCsvIfExists(path.join(jlptDir, `n${n}.csv`));
    rows.forEach((row) => addJlpt(levels, row.expression, `N${n}`));
  }
  const elzupRows = await readCsvIfExists(path.join(jlptDir, "elzup_all.csv"));
  elzupRows.forEach((row) => {
    for (const tag of String(row.tags ?? "").split(/\s+/)) {
      if (tag.startsWith("JLPT_") && tag !== "JLPT") {
        const suffix = tag.split("_", 2)[1];
        addJlpt(levels, row.expression, suffix.startsWith("N") ? suffix : `N${suffix}`);
      }
    }
  });
  const bluskyoRows = await readCsvIfExists(path.join(jlptDir, "bluskyo_all.csv"));
  bluskyoRows.forEach((row) => addJlpt(levels, row.Word, row.JLPTLevel));
  for (let n = 1; n <= 5; n += 1) {
    const rows = await readCsvIfExists(path.join(jlptDir, `coolmule0_n${n}.csv`));
    rows.forEach((row) => {
      addJlpt(levels, row.kanji, `N${n}`);
      addJlpt(levels, row.kana, `N${n}`);
    });
  }
  const wordfreqRows = await readCsvIfExists(path.join(jlptDir, "wordfreq_ja.csv"));
  wordfreqRows.forEach((row) => {
    const expression = String(row.expression ?? "").trim();
    const level = String(row.level ?? "").trim();
    if (expression && /^N[1-5]$/.test(level) && !levels.has(expression)) {
      levels.set(expression, level);
    }
  });
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
    searchText: group.original.toLowerCase()
  })).sort((a, b) => b.sourceCount - a.sourceCount || a.original.localeCompare(b.original, "ja"));

  const sentences = entries.filter((entry) => entry.entryType === "sentence").map((entry) => ({
    ...sourceSummary(entry),
    original: entry.original,
    yasashii: entry.yasashii,
    searchText: [
      entry.original,
      entry.notes,
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
  const json = JSON.stringify(payload).replaceAll("</", "<\\/");
  return `import type { AppPayload } from "../types";\n\nexport const appData = ${json} satisfies AppPayload;\n`;
}

export async function buildData({
  dataDir = path.join(rootDir, "data"),
  output = path.join(rootDir, "src/generated/app-data.ts")
} = {}) {
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
