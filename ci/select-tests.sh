#!/bin/sh
# Run only the tests that the changes since BASE reach.
#   sh ci/select-tests.sh origin/main
# Falls back to the whole suite when it cannot tell (no code changed that the graph knows, or an error).
set -e
BASE=${1:-origin/main}
FULL="python3 -m pytest -q"

axiomcode index > /dev/null
axiomcode tests --range "$BASE..HEAD" --json > selection.json || { echo "selection failed: whole suite"; exec $FULL; }

CMD=$(python3 -c '
import json, sys
s = json.load(open("selection.json"))
changed = [c["symbol"] for c in s["changed"]]
print("changed:", ", ".join(changed) or "nothing the graph indexes", file=sys.stderr)
print("selected:", ", ".join(s["test_files"]) or "none", file=sys.stderr)
print(s["command"] or "")
')

if [ -z "$CMD" ]; then
  echo "no test reaches the change: whole suite"
  exec $FULL
fi
echo "running: $CMD"
exec sh -c "$CMD"
