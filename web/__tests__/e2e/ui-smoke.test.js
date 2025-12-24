import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

test("index.html includes key UI anchors", async () => {
  const html = await readFile(resolve("web/index.html"), "utf-8");
  const requiredIds = [
    "folder-tree",
    "label-tree",
    "tool-list",
    "tool-form",
    "search-form",
  ];

  requiredIds.forEach((id) => {
    assert.ok(html.includes(`id=\"${id}\"`), `Expected to find id ${id}`);
  });
});
