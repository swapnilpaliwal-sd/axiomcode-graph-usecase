-- S4  Every admin endpoint checks that the caller is an admin.
-- every handler in src/handlers/admin.ts  =>  it reaches requireAdmin
-- kind: requires
SELECT h.name AS subject, h.file, h.line,
       CASE WHEN EXISTS (SELECT 1 FROM reaches WHERE src = h.id AND target = 'src/auth#requireAdmin')
            THEN 'ok' ELSE 'violation' END AS verdict,
       (SELECT asserted FROM reaches WHERE src = h.id AND target = 'src/auth#requireAdmin') AS via_link,
       'admin endpoint; must reach requireAdmin' AS why
FROM handler h
WHERE h.file = 'src/handlers/admin.ts';
