-- S2  Every deletion of a note is written to the audit log.
-- every handler that reaches SqlNoteStore.remove  =>  it reaches audit
-- kind: requires
SELECT h.name AS subject, h.file, h.line,
       CASE WHEN EXISTS (SELECT 1 FROM reaches WHERE src = h.id AND target = 'src/audit#audit')
            THEN 'ok' ELSE 'violation' END AS verdict,
       (SELECT asserted FROM reaches WHERE src = h.id AND target = 'src/audit#audit') AS via_link,
       'deletes notes; must reach audit' AS why
FROM handler h
WHERE EXISTS (SELECT 1 FROM reaches WHERE src = h.id AND target = 'src/store#SqlNoteStore.remove');
