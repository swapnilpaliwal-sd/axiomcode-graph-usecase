// A stand-in for a database driver: raw statements, no rules.
export type Row = { id: number; owner: string; text: string };

const table: Row[] = [];

export function exec(sql: string, args: unknown[] = []): Row[] {
  if (sql.startsWith("SELECT")) return table.filter((r) => args.length === 0 || r.owner === args[0]);
  if (sql.startsWith("INSERT")) {
    const row = { id: table.length + 1, owner: String(args[0]), text: String(args[1]) };
    table.push(row);
    return [row];
  }
  if (sql.startsWith("DELETE")) {
    const i = table.findIndex((r) => r.id === args[0]);
    return i < 0 ? [] : table.splice(i, 1);
  }
  throw new Error(`unsupported: ${sql}`);
}

export function reset(): void {
  table.length = 0;
}
