You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `indent(s: &str, prefix: &str) -> String`

## 1. Component overview

Part of `textwrap` 0.11 (a Rust crate for word wrapping, indenting and dedenting text), module
`indentation`, re-exported as `textwrap::indent`. `indent` adds a prefix (for example two spaces,
`"> "` or `"//"`) to the start of every non-empty line of a block of text, similar to Python's
`textwrap.indent`.

## 2. Functional requirements

Lines are the pieces produced by `str::lines`: the text is split at `\n`, a `\r` immediately
before a `\n` is not part of the line, and a final `\n` does not start an extra empty line.
A line is **blank** if it contains no character for which `char::is_whitespace` is false
(Unicode whitespace: space, `\t`, U+00A0, U+3000, ...; the empty line is blank).

For each line, in order:
1. If the line is non-blank, emit `prefix` followed by the line unchanged (its own leading and
   trailing whitespace is kept).
2. If the line is blank, emit nothing for it (its whitespace is dropped and no prefix is added).
3. After every line, emit exactly one `\n` - including after the last line, even when the input
   did not end with a newline.

## 3. Input specification

- `s: &str` - any UTF-8 text, possibly empty, with or without a trailing newline, possibly with
  `\r\n` line endings.
- `prefix: &str` - any string, possibly empty, inserted verbatim.

## 4. Output specification

- A newly allocated `String`. Neither argument is modified; the function is pure and thread-safe.
- The output has exactly one `\n` per input line and always ends with `\n` unless the input has
  no lines (empty input gives `""`).

Examples (Rust string literal notation):

| `s` | `prefix` | output |
|---|---|---|
| `"\n"` | `"  "` | `"\n"` |
| `""` | `"> "` | `""` |
| `"  foo\nbar\n  baz\n"` | `"//"` | `"//  foo\n//bar\n//  baz\n"` |
| `"  foo\nbar\n\n  baz\n"` | `"//"` | `"//  foo\n//bar\n\n//  baz\n"` |
| `"\nFoo\nBar\n"` | `"  "` | `"\n  Foo\n  Bar\n"` |
| `"\nFoo\n\nBar\n  \t\nBaz\n"` | `"->"` | `"\n->Foo\n\n->Bar\n\n->Baz\n"` |
| `" \t  Foo   "` | `"->"` | `"-> \t  Foo   \n"` |
| `"a\nb"` | `"> "` | `"> a\n> b\n"` |
| `"\n\n"` | `"> "` | `"\n\n"` |
| `"a\r\n \t\nb"` | `">"` | `">a\n\n>b\n"` |
| `"\u{a0}\n"` | `">"` | `"\n"` |

## 5. Edge cases and constraints

- Empty `prefix`: non-blank lines are copied unchanged, blank lines become empty, `\r\n`
  becomes `\n`, and a trailing `\n` is ensured.
- `\r\n` line endings are normalised to `\n` in the output.
- Must not panic on any valid UTF-8 input.
- Runtime should be linear in the total output length.

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
dedent s : & str
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
indent_empty
indent_empty_line
indent_nonempty
```

=== STUB ===
```rust
pub fn indent(s: &str, prefix: &str) -> String {
    // TODO: implement according to the specification
}
```
