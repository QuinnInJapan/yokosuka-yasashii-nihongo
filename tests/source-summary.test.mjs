import assert from "node:assert/strict";
import test from "node:test";

import { formatSourceSummary } from "../src/source-summary.ts";

test("formatSourceSummary shows all sources when under the cap", () => {
  assert.equal(formatSourceSummary(["A", "B"], 3), "A、B");
});

test("formatSourceSummary caps sources and appends remaining count", () => {
  assert.equal(formatSourceSummary(["A", "B", "C", "D"], 2), "A、B、他2件");
});

test("formatSourceSummary removes blank names", () => {
  assert.equal(formatSourceSummary(["A", "", "B"], 3), "A、B");
});
