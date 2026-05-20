import assert from "node:assert/strict";
import test from "node:test";

import { groupTermsByHeadword } from "../src/term-groups.ts";

test("groupTermsByHeadword groups renderings under the same original", () => {
  const groups = groupTermsByHeadword([
    {
      original: "津波",
      yasashii: "大きい波",
      sourceCount: 2,
      sourceOrgs: ["A", "B"],
      sourceShortNames: ["A", "B"],
      sourceCategories: [],
      domains: [],
      notes: [],
      retainOriginal: false,
      isNegativeExample: false,
      sources: [],
      jlpt: "",
      searchText: ""
    },
    {
      original: "津波",
      yasashii: "とても高い波",
      sourceCount: 3,
      sourceOrgs: ["A", "C", "D"],
      sourceShortNames: ["A", "C", "D"],
      sourceCategories: [],
      domains: [],
      notes: [],
      retainOriginal: true,
      isNegativeExample: false,
      sources: [],
      jlpt: "",
      searchText: ""
    }
  ]);

  assert.equal(groups.length, 1);
  assert.equal(groups[0].original, "津波");
  assert.equal(groups[0].terms.length, 2);
  assert.equal(groups[0].sourceCount, 4);
  assert.equal(groups[0].retainOriginal, true);
});

test("groupTermsByHeadword sorts groups by source spread", () => {
  const groups = groupTermsByHeadword([
    {
      original: "届出",
      yasashii: "知らせる",
      sourceCount: 1,
      sourceOrgs: ["A"],
      sourceShortNames: ["A"],
      sourceCategories: [],
      domains: [],
      notes: [],
      retainOriginal: false,
      isNegativeExample: false,
      sources: [],
      jlpt: "",
      searchText: ""
    },
    {
      original: "避難",
      yasashii: "逃げる",
      sourceCount: 2,
      sourceOrgs: ["A", "B"],
      sourceShortNames: ["A", "B"],
      sourceCategories: [],
      domains: [],
      notes: [],
      retainOriginal: false,
      isNegativeExample: false,
      sources: [],
      jlpt: "",
      searchText: ""
    }
  ]);

  assert.deepEqual(groups.map((group) => group.original), ["避難", "届出"]);
});
