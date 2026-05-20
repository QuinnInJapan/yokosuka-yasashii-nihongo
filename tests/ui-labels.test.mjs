import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("retain-original labels are not shown in the app UI", async () => {
  const appSource = await readFile("src/App.tsx", "utf8");
  assert.equal(appSource.includes("原語保持"), false);
  assert.equal(appSource.includes("原語を残す"), false);
});

test("sentence rows do not repeat conversion labels from group headings", async () => {
  const appSource = await readFile("src/App.tsx", "utf8");
  assert.equal(appSource.includes("やさしくされた"), false);
  assert.equal(appSource.includes("conversionLabel"), false);
});

test("sentence group headings do not repeat the query match context", async () => {
  const appSource = await readFile("src/App.tsx", "utf8");
  const groupingSource = await readFile("src/sentence-groups.ts", "utf8");
  assert.equal(appSource.includes("原文に検索語"), false);
  assert.equal(groupingSource.includes("${query} →"), false);
});

test("sentence expansion is controlled per group", async () => {
  const appSource = await readFile("src/App.tsx", "utf8");
  assert.equal(appSource.includes("expandedSentenceGroups"), true);
  assert.equal(appSource.includes("文例をすべて見る"), false);
});

test("sentence pattern overview is not shown", async () => {
  const appSource = await readFile("src/App.tsx", "utf8");
  const styles = await readFile("src/styles.css", "utf8");
  assert.equal(appSource.includes("SentencePatternSummary"), false);
  assert.equal(appSource.includes("文例パターン"), false);
  assert.equal(styles.includes("pattern-overview"), false);
});

test("results pane scrolls instead of sticky search panel", async () => {
  const styles = await readFile("src/styles.css", "utf8");
  assert.equal(styles.includes("position: sticky"), false);
  assert.match(styles, /#app\s*{\s*height:\s*100%/s);
  assert.match(styles, /body\s*{[^}]*overflow:\s*hidden/s);
  assert.match(styles, /\.results-stack\s*{[^}]*overflow:\s*auto/s);
  assert.match(styles, /\.results-stack\s*{[^}]*border-top:\s*3px solid var\(--line-strong\)/s);
  assert.equal(styles.includes("border-top: 3px solid var(--accent)"), false);
  assert.match(styles, /scroll-margin-top:\s*16px/);
});

test("section headings use a short marker instead of a full-width rule", async () => {
  const styles = await readFile("src/styles.css", "utf8");
  assert.equal(styles.includes(".section-title {\n  border-top"), false);
  assert.match(styles, /\.section-title::before\s*{[^}]*width:\s*38px/s);
});
