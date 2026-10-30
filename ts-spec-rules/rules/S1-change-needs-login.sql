-- S1  Only a logged-in user can change notes.
-- every handler that reaches SqlNoteStore.add or .remove  =>  it reaches requireUser
-- kind: requires
SELECT h.name AS subject, h.file, h.line,
       CASE WHEN EXISTS (SELECT 1 FROM reaches WHERE src = h.id AND target = 'src/auth#requireUser')
            THEN 'ok' ELSE 'violation' END AS verdict,
       (SELECT asserted FROM reaches WHERE src = h.id AND target = 'src/auth#requireUser') AS via_link,
       'changes notes; must reach requireUser' AS why
FROM handler h
WHERE EXISTS (SELECT 1 FROM reaches WHERE src = h.id
              AND target IN ('src/store#SqlNoteStore.add', 'src/store#SqlNoteStore.remove'));
