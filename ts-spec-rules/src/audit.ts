import { whenDeleted } from "./hooks.ts";

export const AUDIT: string[] = [];

export function audit(action: string, user: string, id: number): void {
  AUDIT.push(`${user} ${action} ${id}`);
}

function auditDeletion(user: string, id: number): void {
  audit("delete", user, id);
}

whenDeleted(auditDeletion);
