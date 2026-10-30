-- Shared words every rule is written in. Read from the OSS graph (.axiomcode/out/graph.sqlite).

-- a function of this repository (not a library)
CREATE TEMP VIEW fn AS
  SELECT id, qualified_name AS name, file_path AS file, start_line AS line
  FROM methods WHERE provenance != 'lib' AND name NOT LIKE '<%';

-- a handler: a function in src/handlers/
CREATE TEMP VIEW handler AS
  SELECT * FROM fn WHERE file LIKE 'src/handlers/%';

-- a call the graph knows the target of, and how it knows (tier)
CREATE TEMP VIEW edge AS
  SELECT caller_id AS src, callee_method_id AS dst, tier FROM call_edges
  WHERE callee_method_id IS NOT NULL
    AND tier IN ('known_edge', 'multi_inferred', 'callback_registered', 'asserted');

-- A reaches B through one or more known calls; `asserted` is set when any hop is an agent's link
CREATE TEMP VIEW reach AS
  WITH RECURSIVE r(src, dst, asserted) AS (
    SELECT src, dst, tier = 'asserted' FROM edge
    UNION
    SELECT r.src, e.dst, r.asserted OR e.tier = 'asserted' FROM r JOIN edge e ON e.src = r.dst
  )
  SELECT src, dst, MAX(asserted) AS asserted FROM r GROUP BY src, dst;

-- A reaches the function named N (by qualified name, e.g. 'src/audit#audit')
CREATE TEMP VIEW reaches AS
  SELECT r.src, f.name AS target, MIN(r.asserted) AS asserted
  FROM reach r JOIN fn f ON f.id = r.dst GROUP BY r.src, f.name;

-- calls whose target the graph does not know, inside a function or anything it reaches: where a rule's answer may be
-- wrong. kind 'value': a call through a function-typed value (a callback list, a handler map) that no link settles;
-- 'unresolved': any other
CREATE TEMP VIEW blind AS
  WITH inside(src, m) AS (SELECT id, id FROM fn UNION SELECT src, dst FROM reach)
  SELECT i.src, s.callee_name AS written, s.file_path AS file, s.start_line AS line, s.start_column AS col, 'value' AS kind
  FROM inside i
  JOIN call_edges e ON e.caller_id = i.m
  JOIN methods t ON t.id = e.callee_method_id AND t.name LIKE '<function-type>%'
  JOIN call_sites s ON s.id = e.call_site_id
  WHERE NOT EXISTS (SELECT 1 FROM call_edges a WHERE a.call_site_id = e.call_site_id AND a.tier = 'asserted')
  UNION
  SELECT i.src, s.callee_name, s.file_path, s.start_line, s.start_column, 'unresolved'
  FROM inside i
  JOIN unresolved_sites u ON u.caller_id = i.m
  JOIN call_sites s ON s.id = u.call_site_id;
