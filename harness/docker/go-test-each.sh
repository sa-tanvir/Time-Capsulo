#!/bin/bash
# Run every top-level Test*/Example* of every package in its own test-binary process and
# append `go test -json`-style events (via test2json) to $OUT (default /out/go-test.json).
# Isolation matters for sabotage: a stub panics, and in a shared process a panic would
# abort every later test in the package. Never stops at the first failure.
# Usage: go-test-each [pkg-pattern ...]   (default ./...)
OUT=${OUT:-/out/go-test.json}
TIMEOUT=${TC_TEST_TIMEOUT:-60s}
BIN=$(mktemp -d)
: > "$OUT"
pkgs=$(go list -f '{{.ImportPath}}|{{.Dir}}' "${@:-./...}") || exit 2
built=0
for pd in $pkgs; do
  pkg=${pd%%|*}; dir=${pd#*|}
  # binary named <last-elem>.test like `go test` does (cobra checks os.Args[0] == "cobra.test")
  sub="$BIN/$(echo "$pkg" | tr '/.' '__')"; mkdir -p "$sub"
  exe="$sub/${pkg##*/}.test"
  if ! go test -c -o "$exe" "$pkg" 2>&1; then
    echo "BUILD FAILED: $pkg"
    continue
  fi
  [ -x "$exe" ] || continue          # package without test files
  built=1
  for t in $(cd "$dir" && "$exe" -test.list '.*' | grep -E '^(Test|Example)'); do
    (cd "$dir" && go tool test2json -p "$pkg" "$exe" -test.v -test.timeout "$TIMEOUT" -test.run "^${t}\$") >> "$OUT" 2>/dev/null
  done
done
rm -rf "$BIN"
[ $built = 1 ] || exit 2
exit 0
