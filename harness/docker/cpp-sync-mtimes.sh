#!/bin/bash
# usage: tc-sync-mtimes <manifest> <dir-or-file>...
# Touch files whose content hash differs from the one recorded in <manifest>, then rewrite it.
set -e
man="$1"; shift
new="$(mktemp)"
find "$@" -type f \( -name '*.h' -o -name '*.hpp' -o -name '*.hh' -o -name '*.c' -o -name '*.cc' -o -name '*.cpp' -o -name '*.cxx' -o -name '*.inl' -o -name '*.ipp' \) -print0 \
  | sort -z | xargs -0 md5sum > "$new"
if [ -f "$man" ]; then
  # lines in new but not in old -> changed or new files
  comm -13 "$man" "$new" | sed 's/^[0-9a-f]*  //' | while IFS= read -r f; do touch -- "$f"; done
fi
mv "$new" "$man"
