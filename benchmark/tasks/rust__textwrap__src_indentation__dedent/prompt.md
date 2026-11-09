You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `dedent(s: &str) -> String`

## 1. Component overview

Part of `textwrap` 0.11 (a Rust crate for word wrapping, indenting and dedenting text), module
`indentation`, re-exported as `textwrap::dedent`. `dedent` removes the leading whitespace that is
common to the lines of a block of text, similar to Python's `textwrap.dedent`. It is the inverse
companion of `indent` in the same module.

## 2. Functional requirements

Terminology: a line is **blank** if it contains no character for which `char::is_whitespace`
is false (this includes the empty line). Whitespace is Unicode whitespace as defined by
`char::is_whitespace` (space, `\t`, U+00A0 no-break space, U+3000, ...). Lines are the pieces
produced by `str::lines` (split at `\n`; a `\r` immediately before the `\n` is not part of the line;
a final `\n` does not start an extra empty line).

1. **Determine the common prefix.**
   - The initial prefix is the run of leading whitespace characters of the **first non-blank line**.
     Blank lines that come *before* that line are ignored for the prefix.
   - Every line that comes *after* that first non-blank line (blank or not) can shorten the prefix:
     compare the line with the current prefix character by character from the start. If a
     differing character is found at a position that is strictly inside the line (i.e. before the
     end of the line) and strictly inside the current prefix, the prefix becomes the part of the
     line before that position. If the line ends before any difference is found (the line is
     itself an initial part of the prefix), or the prefix is exhausted without a difference, the
     prefix is unchanged.
   - Characters are compared exactly: a tab never matches a space, NBSP never matches a space.
   - If there is no non-blank line, the prefix is empty.
2. **Build the output.** For each line, in order:
   - if the line is non-blank (and starts with the prefix), emit the line with the prefix removed;
   - if the line is blank, emit nothing for its content (all of its whitespace is dropped);
   - then emit a single `\n`.
3. **Final newline.** If the produced text ends with `\n` but the input `s` does not end with `\n`,
   remove that one trailing `\n`. Otherwise keep it.

Consequences: line terminators in the output are always `\n` (`\r\n` input becomes `\n`);
relative indentation between lines is preserved; whitespace *after* the first non-whitespace
character of a line is never touched.

## 3. Input specification

- `s: &str` - any UTF-8 text, possibly empty, possibly multi-line, with or without a trailing
  newline, possibly using `\r\n` line endings, and possibly mixing whitespace kinds.

## 4. Output specification

- A newly allocated `String` as described above. The input is not modified. The function is pure
  and thread-safe.

Examples (Rust string literal notation):

| input | output |
|---|---|
| `""` | `""` |
| `"\n"` | `"\n"` |
| `"   "` | `""` |
| `"    foo\n  bar\n    baz\n"` | `"  foo\nbar\n  baz\n"` |
| `"    foo\n  bar\n   \n    baz\n"` | `"  foo\nbar\n\n  baz\n"` |
| `"      foo\n\n        bar\n          foo\n"` | `"foo\n\n  bar\n    foo\n"` |
| `"      foo\n \n        bar\n"` | `"foo\n\n  bar\n"` |
| `"\tfoo\n  bar\n"` | `"\tfoo\n  bar\n"` (no common prefix) |
| `"\t\tfoo\n\t\t\tbar\n"` | `"foo\n\tbar\n"` |
| `"\t  \tfoo\n\t  \t\tbar\n"` | `"foo\n\tbar\n"` |
| `"\t  \tfoo\n\t    \tbar\n"` | `"\tfoo\n  \tbar\n"` |
| `"  foo\n    bar"` | `"foo\n  bar"` (no final newline added) |
| `"\n    1st line\n      2nd line\n    3rd line\n"` | `"\n1st line\n  2nd line\n3rd line\n"` |
| `"  \n    a\n  b\n"` | `"\n  a\nb\n"` (leading blank line ignored for the prefix) |
| `"    a\n \t\n    b\n"` | `"   a\n\n   b\n"` (blank line after the first non-blank line shortens the prefix to `" "`) |
| `"    a\n  \n    b\n"` | `"a\n\nb\n"` (blank line `"  "` is an initial part of the prefix: no change) |
| `"  a\r\n    b\r\n"` | `"a\n  b\n"` |
| `"\u{a0}\u{a0}a\n\u{a0}\u{a0}\u{a0}b"` | `"a\n\u{a0}b"` |
| `"a\n\n"` | `"a\n\n"` |

## 5. Edge cases and constraints

- Empty input returns the empty string.
- Input consisting only of blank lines returns one `\n` per line (minus the final one if the input
  did not end with `\n`).
- Lines that become blank keep their place as empty lines.
- Must not panic on any valid UTF-8 input; slicing must respect character boundaries (prefix
  lengths are measured in bytes of whole characters).
- Runtime should be linear in the length of `s`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/indentation.rs`

## Imports / includes available in this file

```
    use super::*;
```

## Other functions defined in the same file (signatures only; you may call them)

```
add_nl lines : & [ & str ]
dedent_blank_line
dedent_empty
dedent_empty_line
dedent_mixed_tabbed_whitespace
dedent_mixed_tabbed_whitespace2
dedent_mixed_whitespace
dedent_multi_line
dedent_preserve_no_terminating_newline
dedent_tabbed_whitespace
dedent_whitespace_line
indent s : & str , prefix : & str
indent_empty
indent_empty_line
indent_nonempty
```

=== STUB ===
```rust
pub fn dedent(s: &str) -> String {
    // TODO: implement according to the specification
}
```
