-- S3  Only the store (src/store.ts) talks to the database driver.
-- never: a function outside src/store.ts and src/driver.ts calls exec directly
-- kind: forbids
SELECT f.name AS subject, f.file, f.line,
       CASE WHEN f.file IN ('src/store.ts', 'src/driver.ts') THEN 'ok' ELSE 'violation' END AS verdict,
       'calls the driver directly' AS why
FROM fn f
WHERE EXISTS (SELECT 1 FROM edge e JOIN fn t ON t.id = e.dst
              WHERE e.src = f.id AND t.name = 'src/driver#exec');
