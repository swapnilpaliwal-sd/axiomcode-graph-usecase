// Runs every rules/S*.sql against the OSS graph and reports each requirement as ok, violation or unsure.
// Usage: axiomcode index && node rules/check.ts
import { DatabaseSync } from "node:sqlite";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

type Row = { subject: string; file: string; line: number; verdict: string; why: string; via_link?: number | null };

const dir = new URL(".", import.meta.url).pathname;
const db = new DatabaseSync(join(dir, "..", ".axiomcode/out/graph.sqlite"), { readOnly: true });
db.exec(readFileSync(join(dir, "_views.sql"), "utf8"));

const blindOf = db.prepare(
  "SELECT DISTINCT written, file, line, col, kind FROM blind WHERE src = (SELECT id FROM fn WHERE name = ?) ORDER BY kind DESC, file, line",
);
const blindInSrc = db.prepare(
  "SELECT count(*) AS n FROM unresolved_sites u JOIN call_sites s ON s.id = u.call_site_id WHERE s.file_path LIKE 'src/%'",
);

let failed = 0;
for (const file of readdirSync(dir).filter((f) => /^S\d.*\.sql$/.test(f)).sort()) {
  const sql = readFileSync(join(dir, file), "utf8");
  const title = sql.split("\n")[0].replace(/^--\s*/, "");
  const forbids = /-- kind: forbids/.test(sql);
  const rows = (db.prepare(sql).all() as Row[]).sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line);
  const bad = rows.filter((r) => r.verdict === "violation");
  const head = rows.length === 0 ? "checked nothing (not a pass: no code matched the rule's words)"
    : bad.length ? `checked ${rows.length} · ${bad.length} violation(s)` : `checked ${rows.length} · all ok`;
  console.log(`${bad.length ? "✗" : rows.length ? "✓" : "?"} ${title}\n    ${head}`);
  for (const r of rows) {
    const mark = r.verdict === "ok" ? "ok  " : "FAIL";
    const link = r.via_link ? "  [through an asserted link]" : "";
    console.log(`    ${mark} ${r.subject}  ${r.file}:${r.line}  ${r.verdict === "ok" ? "" : r.why}${link}`);
    if (r.verdict === "violation" && !forbids) {
      type Blind = { written: string; file: string; line: number; col: number; kind: string };
      const sites = blindOf.all(r.subject) as Blind[];
      const values = sites.filter((b) => b.kind === "value");
      const others = sites.filter((b) => b.kind !== "value").map((b) => b.written);
      if (sites.length) console.log("         unsure: the graph could not follow these calls on the way; the required call may hide behind one:");
      for (const b of values) console.log(`           ${b.file}:${b.line}:${b.col}  ${b.written}(…)  a call through a function-typed value`);
      if (others.length) console.log(`           ${values.length ? "+ " : ""}${others.length} ${values.length ? "other " : ""}unresolved call site(s), named: ${[...new Set(others)].join(", ")}`);
      if (sites.length) console.log("         read them; if one makes the target certain: axiomcode link <file:line:col> <target>, then re-check");
    }
  }
  if (forbids) {
    const n = (blindInSrc.get() as { n: number }).n;
    if (n) console.log(`    lower bound: ${n} unresolved call site(s) in src/; a caller hidden behind one of them is not listed`);
  }
  if (rows.length === 0) failed++;
  failed += bad.length;
  console.log("");
}
console.log(failed ? `${failed} problem(s)` : "all requirements hold");
process.exit(failed ? 1 : 0);
