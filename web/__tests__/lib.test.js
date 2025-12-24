import test from "node:test";
import assert from "node:assert/strict";
import { buildFolderTree, buildToolQueryParams } from "../lib.js";

test("buildFolderTree nests folders and preserves roots", () => {
  const folders = [
    { id: "1", name: "Root" },
    { id: "2", name: "Child", parentId: "1" },
    { id: "3", name: "Other" },
  ];

  const tree = buildFolderTree(folders);
  assert.equal(tree.length, 2);
  const root = tree.find((node) => node.id === "1");
  assert.ok(root);
  assert.equal(root.children.length, 1);
  assert.equal(root.children[0].id, "2");
});

test("buildToolQueryParams includes provided filters", () => {
  const params = buildToolQueryParams({
    search: "agent",
    folderPath: "/eng",
    labels: ["alpha", "beta"],
  });

  assert.equal(params, "search=agent&folderPath=%2Feng&labels=alpha%2Cbeta");
});

test("buildToolQueryParams returns empty string without filters", () => {
  assert.equal(buildToolQueryParams(), "");
});
