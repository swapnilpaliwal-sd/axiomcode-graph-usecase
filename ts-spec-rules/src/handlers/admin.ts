import { requireAdmin, type Request } from "../auth.ts";
import type { NoteStore } from "../store.ts";

export function exportAll(store: NoteStore, req: Request) {
  requireAdmin(req);
  return store.all();
}
