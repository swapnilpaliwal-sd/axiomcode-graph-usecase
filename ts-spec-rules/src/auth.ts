export type Request = { user?: string; role?: "user" | "admin"; params: Record<string, string>; body?: any };

export class Forbidden extends Error {}

export function requireUser(req: Request): string {
  if (!req.user) throw new Forbidden("login required");
  return req.user;
}

export function requireAdmin(req: Request): string {
  const user = requireUser(req);
  if (req.role !== "admin") throw new Forbidden("admin only");
  return user;
}
