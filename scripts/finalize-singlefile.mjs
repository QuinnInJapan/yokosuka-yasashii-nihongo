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
