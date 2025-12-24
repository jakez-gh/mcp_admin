import test from "node:test";
import assert from "node:assert/strict";
import { apiRequest } from "../../api.js";

test("apiRequest returns json payload", async () => {
  const expected = { ok: true };
  global.fetch = async (url, options) => {
    assert.equal(url, "/api/tools");
    assert.equal(options.method, "GET");
    return {
      ok: true,
      status: 200,
      json: async () => expected,
    };
  };

  const result = await apiRequest("/api/tools", { method: "GET" });
  assert.deepEqual(result, expected);
});

test("apiRequest handles 204 responses", async () => {
  global.fetch = async () => ({
    ok: true,
    status: 204,
    text: async () => "",
  });

  const result = await apiRequest("/api/tools", { method: "DELETE" });
  assert.equal(result, null);
});

test("apiRequest throws on errors", async () => {
  global.fetch = async () => ({
    ok: false,
    status: 500,
    text: async () => "Boom",
  });

  await assert.rejects(
    () => apiRequest("/api/tools"),
    (error) => error instanceof Error && error.message === "Boom",
  );
});
