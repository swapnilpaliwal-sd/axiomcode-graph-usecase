#!/bin/sh
# Export the graph's functions and calls as Datalog facts, then run the rule.
set -e
db=.axiomcode/out/graph.sqlite
facts=.axiomcode/facts
mkdir -p "$facts"
sqlite3 -separator '	' "$db" "SELECT id, name, file_path, start_line FROM methods" > "$facts/method.facts"
sqlite3 -separator '	' "$db" "SELECT caller_id, callee_method_id FROM call_edges WHERE callee_method_id IS NOT NULL" > "$facts/calls.facts"
souffle -F "$facts" spec.dl
