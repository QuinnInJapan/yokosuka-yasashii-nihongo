import assert from "node:assert/strict";
import test from "node:test";

import { getHighlightParts } from "../src/text-highlight.ts";

test("getHighlightParts marks query matches", () => {
  assert.deepEqual(getHighlightParts("津波（大きな波）", "津波"), [
    { text: "津波", match: true },
    { text: "（大きな波）", match: false }
  ]);
});

test("getHighlightParts is case-insensitive for latin text", () => {
  assert.deepEqual(getHighlightParts("Hello HELLO", "hello"), [
    { text: "Hello", match: true },
    { text: " ", match: false },
    { text: "HELLO", match: true }
  ]);
});

test("getHighlightParts returns plain text for blank query", () => {
  assert.deepEqual(getHighlightParts("津波", ""), [
    { text: "津波", match: false }
  ]);
});
