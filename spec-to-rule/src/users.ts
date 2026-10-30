import { removeUser } from "./db.ts";
import { audit } from "./audit.ts";

export function banUser(id: number): void {
  removeUser(id);
  audit(`banned ${id}`);
}

export function deleteUser(id: number): void {
  removeUser(id);
}
