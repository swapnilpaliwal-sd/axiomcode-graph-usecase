import { exec, type Row } from "./driver.ts";

export interface NoteStore {
  list(owner: string): Row[];
  add(owner: string, text: string): Row;
  remove(id: number): boolean;
  all(): Row[];
}

export class SqlNoteStore implements NoteStore {
  list(owner: string): Row[] {
    return exec("SELECT * FROM notes WHERE owner = ?", [owner]);
  }

  add(owner: string, text: string): Row {
    return exec("INSERT INTO notes (owner, text) VALUES (?, ?)", [owner, text])[0];
  }

  remove(id: number): boolean {
    return exec("DELETE FROM notes WHERE id = ?", [id]).length > 0;
  }

  all(): Row[] {
    return exec("SELECT * FROM notes");
  }
}
