import assert from "node:assert/strict";
import test from "node:test";

import { scoreTerm } from "../src/search.ts";

const baseTerm = {
  original: "津波",
  yasashii: "大きな波",
  sourceCount: 3,
  sourceOrgs: ["川崎市"],
  sourceShortNames: ["川崎市GL"],
  sourceCategories: [],
  domains: [],
  notes: ["用語解説"],
  retainOriginal: false,
  isNegativeExample: false,
  sources: [],
  jlpt: "",
  searchText: "津波"
};

test("scoreTerm matches exact headword", () => {
  assert.ok(scoreTerm(baseTerm, "津波") > 0);
});

test("scoreTerm matches partial headword", () => {
  assert.ok(scoreTerm(baseTerm, "津") > 0);
});

test("scoreTerm does not match yasashii rendering", () => {
  assert.equal(scoreTerm(baseTerm, "大きな波"), 0);
});

test("scoreTerm does not match source names or notes", () => {
  assert.equal(scoreTerm(baseTerm, "川崎市"), 0);
  assert.equal(scoreTerm(baseTerm, "用語解説"), 0);
});
