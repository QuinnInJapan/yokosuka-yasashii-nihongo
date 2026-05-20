import assert from "node:assert/strict";
import test from "node:test";

import { groupSentenceEvidence } from "../src/sentence-groups.ts";

function sentence(overrides) {
  return {
    sourceId: "01",
    sourceOrg: "川崎市",
    sourceDocument: "文書A",
    sourceDate: "2023",
    sourceShortName: "川崎市GL",
    sourceCategory: "行政",
    sourceUrl: "",
    domains: ["防災"],
    notes: "",
    retainOriginal: false,
    isNegativeExample: false,
    original: "",
    yasashii: "",
    searchText: "",
    ...overrides,
  };
}

test("groupSentenceEvidence groups original-side matches by known conversion pattern", () => {
  const groups = groupSentenceEvidence([
    sentence({ original: "津波が来ます", yasashii: "大きな波が来ます" }),
    sentence({ original: "津波に注意してください", yasashii: "大きな波に気をつけてください", sourceShortName: "大阪府手引き" }),
    sentence({ original: "津波から逃げてください", yasashii: "高い波から逃げてください" }),
  ], "津波", ["大きな波", "高い波"]);

  assert.equal(groups[0].label, "大きな波");
  assert.equal(groups[0].count, 2);
  assert.deepEqual(groups[0].sourceShortNames, ["川崎市GL", "大阪府手引き"]);
  assert.equal(groups[1].label, "高い波");
  assert.equal(groups[1].count, 1);
});

test("groupSentenceEvidence keeps output-only matches in related evidence", () => {
  const groups = groupSentenceEvidence([
    sentence({ original: "津波が来ます", yasashii: "津波が来ます" }),
    sentence({ original: "大きな波が来ます", yasashii: "津波が来ます" }),
    sentence({ original: "海の水が来ます", yasashii: "海の水が来ます", notes: "津波関連" }),
  ], "津波", ["大きな波"]);

  assert.deepEqual(groups.map((group) => group.label), [
    "そのまま",
    "関連文例",
  ]);
  assert.deepEqual(groups.map((group) => group.role), ["original", "related"]);
  assert.equal(groups[1].count, 2);
});

test("groupSentenceEvidence ranks rewrites above unchanged examples", () => {
  const groups = groupSentenceEvidence([
    sentence({ original: "津波警報が出ています", yasashii: "津波がくるかもしれません" }),
    sentence({ original: "津波に注意してください", yasashii: "海の近くから逃げてください" }),
    sentence({ original: "津波が来ます", yasashii: "大きな波が来ます" }),
  ], "津波", ["大きな波"]);

  assert.deepEqual(groups.map((group) => group.label), [
    "大きな波",
    "文全体で言い換え",
    "そのまま",
  ]);
});
