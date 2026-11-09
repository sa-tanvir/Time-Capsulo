# Functional specification: `func indentString(s, p string) string`

## 1. Component overview

`indentString` is a helper of package `doc` (`github.com/spf13/cobra/doc`),
which generates documentation (man pages, Markdown, reStructuredText, YAML)
for cobra command trees. The reStructuredText generator uses it to indent a
command's multi-line `Example` text so it forms a literal block, e.g.
`indentString(cmd.Example, "  ")`. The function returns a copy of `s` in which
the prefix `p` has been inserted at the beginning of every **non-empty** line.

## 2. Functional requirements

1. A "line" is a maximal run of bytes not containing `'\n'`; lines are
   separated by single `'\n'` bytes. The first line starts at the beginning of
   `s`; every other line starts right after a `'\n'`.
2. For every line that contains at least one byte, insert `p` immediately
   before its first byte. Empty lines (two consecutive `'\n'`, or a `'\n'` at
   the very start) receive **no** prefix.
3. All bytes of `s`, including every `'\n'`, are kept unchanged and in order.
   Nothing is trimmed and no newline is added or removed.
4. A trailing `'\n'` at the end of `s` does **not** cause a prefix to be
   appended after it (the "line" after it is empty).
5. Only `'\n'` separates lines. `'\r'`, tabs and spaces are ordinary content:
   a line consisting only of `" "` or `"\r"` is non-empty and gets the prefix.
6. Processing is byte-oriented; `s` and `p` may contain arbitrary UTF-8 and are
   copied verbatim.
7. The function is pure and does not modify its arguments.

Examples (Go string literals):

| `s` | `p` | result |
|---|---|---|
| `""` | `"  "` | `""` |
| `"abc"` | `"  "` | `"  abc"` |
| `"a\nb"` | `"  "` | `"  a\n  b"` |
| `"a\nb\n"` | `"> "` | `"> a\n> b\n"` |
| `"a\n\nb"` | `"--"` | `"--a\n\n--b"` |
| `"\nx"` | `"#"` | `"\n#x"` |
| `"\n\n"` | `"#"` | `"\n\n"` |
| `" \n\r\n"` | `"#"` | `"# \n#\r\n"` |
| `"line1\nline2"` | `""` | `"line1\nline2"` |
| `"Just run cobra-test echo"` | `"  "` | `"  Just run cobra-test echo"` |

## 3. Input specification

- `s`: any string (possibly empty, possibly very long, any number of lines).
- `p`: the prefix, any string (possibly empty, possibly multi-byte).

## 4. Output specification

- A new `string`. Its length is `len(s) + k*len(p)`, where `k` is the number
  of non-empty lines of `s`.
- Removing every inserted prefix yields exactly `s`.

## 5. Edge cases and constraints

- Empty `s` returns `""` regardless of `p`.
- Empty `p` returns a string equal to `s`.
- `s` consisting only of newlines is returned unchanged.
- Never panics; no errors.
