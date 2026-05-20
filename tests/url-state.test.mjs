import assert from "node:assert/strict";
import test from "node:test";

import { buildSearchUrl, readSearchQuery } from "../src/url-state.ts";

test("readSearchQuery reads q from a URL search string", () => {
  assert.equal(readSearchQuery("?q=%E9%81%BF%E9%9B%A3"), "避難");
});

test("readSearchQuery returns an empty string when q is missing", () => {
  assert.equal(readSearchQuery("?domain=%E9%98%B2%E7%81%BD"), "");
});

test("buildSearchUrl sets q while preserving other params and hash", () => {
  assert.equal(
    buildSearchUrl("file:///tmp/yasashii-reference.html?domain=防災#top", "避難指示"),
    "file:///tmp/yasashii-reference.html?domain=%E9%98%B2%E7%81%BD&q=%E9%81%BF%E9%9B%A3%E6%8C%87%E7%A4%BA#top"
  );
});

test("buildSearchUrl removes q for a blank query", () => {
  assert.equal(
    buildSearchUrl("file:///tmp/yasashii-reference.html?domain=防災&q=避難#top", "   "),
    "file:///tmp/yasashii-reference.html?domain=%E9%98%B2%E7%81%BD#top"
  );
});
