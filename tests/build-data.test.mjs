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

test("loadEntries trims source and entry text fields", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "yasashii-clean-data-"));
  await writeFile(
    path.join(dir, "sources.csv"),
    "source_id,source_org,source_document,source_url,source_date,source_category,source_description,source_short_name,source_vocab_standard,source_notes\n" +
      "01, 川崎市 , 文書A , https://example.test/a.pdf , 2023 , 行政 ,説明, 川崎市GL ,,注意\n",
    "utf8"
  );
  const entries = [{
    source_id: " 01 ",
    source_org: " 川崎市 ",
    source_document: " 文書A ",
    source_date: " 2023 ",
    domain: " 防災 , 行政手続 ",
    entry_type: " term ",
    original: "  津波  ",
    original_normalized: " 津波 ",
    yasashii: " 大きな波 ",
    notes: " 用語解説 ",
    retain_original: false,
    is_negative_example: false
  }];
  await writeFile(path.join(dir, "01_sample.json"), JSON.stringify(entries), "utf8");

  const [loaded] = await loadEntries(dir, await loadSources(dir));

  assert.equal(loaded.sourceId, "01");
  assert.equal(loaded.sourceOrg, "川崎市");
  assert.equal(loaded.sourceDocument, "文書A");
  assert.equal(loaded.sourceDate, "2023");
  assert.equal(loaded.sourceShortName, "川崎市GL");
  assert.equal(loaded.sourceCategory, "行政");
  assert.deepEqual(loaded.domains, ["防災", "行政手続"]);
  assert.equal(loaded.entryType, "term");
  assert.equal(loaded.original, "津波");
  assert.equal(loaded.originalNormalized, "津波");
  assert.equal(loaded.yasashii, "大きな波");
  assert.equal(loaded.notes, "用語解説");
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

test("buildPayload term search text only contains the headword", () => {
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
      original: "津波",
      originalNormalized: "津波",
      yasashii: "大きな波",
      notes: "用語解説",
      retainOriginal: false,
      isNegativeExample: false
    }
  ], new Map());

  assert.equal(payload.terms[0].searchText, "津波");
});

test("buildPayload sentence search text excludes source names and yasashii output", () => {
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
      entryType: "sentence",
      original: "津波が来ます",
      originalNormalized: "",
      yasashii: "高い水が来ます",
      notes: "用語解説",
      retainOriginal: false,
      isNegativeExample: false
    }
  ], new Map());

  assert.equal(payload.sentences[0].searchText.includes("川崎市"), false);
  assert.equal(payload.sentences[0].searchText.includes("川崎市GL"), false);
  assert.equal(payload.sentences[0].searchText.includes("文書A"), false);
  assert.equal(payload.sentences[0].searchText.includes("高い水"), false);
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
