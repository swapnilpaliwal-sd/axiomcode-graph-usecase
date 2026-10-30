import { requireUser, type Request } from "../auth.ts";
import type { NoteStore } from "../store.ts";
import { audit } from "../audit.ts";
import { deleted } from "../hooks.ts";

export function listNotes(store: NoteStore, req: Request) {
  const user = requireUser(req);
  return store.list(user);
}

export function createNote(store: NoteStore, req: Request) {
  const user = requireUser(req);
  return store.add(user, String(req.body?.text ?? ""));
}

export function deleteNote(store: NoteStore, req: Request) {
  const user = requireUser(req);
  const id = Number(req.params.id);
  const deleted = store.remove(id);
  if (deleted) audit("delete", user, id);
  return { deleted };
}

export function clearNotes(store: NoteStore, req: Request) {
  const user = requireUser(req);
  for (const note of store.list(user)) {
    if (store.remove(note.id)) deleted(user, note.id);
  }
  return { cleared: true };
}
