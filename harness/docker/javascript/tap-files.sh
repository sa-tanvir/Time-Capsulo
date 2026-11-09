#!/bin/bash
# Run each node-tap test file directly with node (no nyc/coverage) and re-emit its
# top-level subtests as "ok 0 - <file> :: <subtest>" TAP lines; every other output
# line is prefixed with "#| " so nested assertion lines are not parsed as tests.
# usage: tap-files.sh test/*.js
for f in "$@"; do
  timeout 300 node "$f" 2>&1 | awk -v f="$f" '
    /^(not )?ok [0-9]+ - / { s = $0; sub(/ # time=.*/, "", s); st = (s ~ /^not ok/) ? "not ok" : "ok";
                             sub(/^(not )?ok [0-9]+ - /, "", s); print st " 0 - " f " :: " s; next }
    { print "#| " $0 }'
done
exit 0
