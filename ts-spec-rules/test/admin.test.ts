import { test } from "node:test";
import assert from "node:assert/strict";
import { handle } from "../src/server.ts";
import { Forbidden } from "../src/auth.ts";

test("export is admin only", () => {
  assert.throws(() => handle("GET /admin/export", { user: "ana", role: "user", params: {} }), Forbidden);
});
