import { type Request } from "./auth.ts";
import { SqlNoteStore, type NoteStore } from "./store.ts";
import { listNotes, createNote, deleteNote, clearNotes } from "./handlers/notes.ts";
import { exportAll } from "./handlers/admin.ts";

type Handler = (store: NoteStore, req: Request) => unknown;

export const routes: Record<string, Handler> = {
  "GET /notes": listNotes,
  "POST /notes": createNote,
  "DELETE /notes/:id": deleteNote,
  "DELETE /notes": clearNotes,
  "GET /admin/export": exportAll,
};

const store: NoteStore = new SqlNoteStore();

export function handle(route: string, req: Request): unknown {
  const handler = routes[route];
  if (!handler) throw new Error(`no route ${route}`);
  return handler(store, req);
}
