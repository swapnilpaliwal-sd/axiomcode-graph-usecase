import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { handle } from "../src/server.ts";
import { reset } from "../src/driver.ts";
import { Forbidden } from "../src/auth.ts";

beforeEach(() => reset());

test("a user creates and lists their notes", () => {
  handle("POST /notes", { user: "ana", params: {}, body: { text: "hi" } });
  assert.deepEqual(handle("GET /notes", { user: "ana", params: {} }), [{ id: 1, owner: "ana", text: "hi" }]);
});

test("deleting needs a login", () => {
  assert.throws(() => handle("DELETE /notes/:id", { params: { id: "1" } }), Forbidden);
});

test("a user deletes a note", () => {
  handle("POST /notes", { user: "ana", params: {}, body: { text: "hi" } });
  assert.deepEqual(handle("DELETE /notes/:id", { user: "ana", params: { id: "1" } }), { deleted: true });
});

test("clearing notes audits each deletion", async () => {
  const { AUDIT } = await import("../src/audit.ts");
  AUDIT.length = 0;
  handle("POST /notes", { user: "ana", params: {}, body: { text: "a" } });
  handle("POST /notes", { user: "ana", params: {}, body: { text: "b" } });
  handle("DELETE /notes", { user: "ana", params: {} });
  assert.deepEqual(AUDIT, ["ana delete 1", "ana delete 2"]);
});
