-- Spec: every function that removes a user also writes to the audit log.
-- Lists every function that calls removeUser but never calls audit. No rows = the spec holds.
SELECT f.name AS breaks_the_spec, f.file_path AS file, f.start_line AS line
FROM methods f
WHERE EXISTS (SELECT 1 FROM call_edges e JOIN methods t ON t.id = e.callee_method_id
              WHERE e.caller_id = f.id AND t.name = 'removeUser')
  AND NOT EXISTS (SELECT 1 FROM call_edges e JOIN methods t ON t.id = e.callee_method_id
                  WHERE e.caller_id = f.id AND t.name = 'audit');
