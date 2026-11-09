# Functional specification: `func squash(json string) string`

## 1. Component overview

`squash` is an internal helper of the `gjson` package (`github.com/tidwall/gjson`),
a library that extracts values from JSON text without fully decoding it. Given a
string whose first character opens a JSON value (an array, an object, a
parenthesised group used by the path syntax, or a string literal), `squash`
returns the prefix of the input that contains exactly that one value, ignoring
whatever follows it. The library uses it to cut the raw text of nested
arrays/objects out of a larger document (e.g. when listing the members of an
array, building `Result.Raw`, or splitting modifier arguments such as
`@pretty:{"sortKeys":true}`).

The function does not validate JSON; it only tracks bracket nesting and string
literals.

## 2. Functional requirements

1. **Bracketed values.** If the first character is anything other than `"`,
   it is treated as the opener: it is skipped without being examined and the
   nesting depth starts at 1. Normally it is `[`, `{` or `(`, but callers also
   pass text whose first character is an ordinary byte (for a multipath such as
   `{a,b}|c`, the library calls `squash("a,b}|c")`, which returns `a,b}`); such
   a first character is treated exactly like an opener. Scanning the following
   characters:
   - any of `[`, `{`, `(` increases the depth by one;
   - any of `]`, `}`, `)` decreases it by one. The kinds are **not** matched
     against each other: `[` may be closed by `}` or `)`.
   - when the depth returns to 0, return the input up to and including that
     closing character.
2. **String literals are opaque.** A `"` outside a string starts a string
   literal. Everything up to its closing quote is skipped, so brackets inside
   strings are ignored. A quote is a closing quote only if it is preceded by an
   **even** number (including zero) of consecutive backslashes inside the
   literal; a quote preceded by an odd number of backslashes is escaped and
   does not end the string. Backslashes have no meaning outside string
   literals.
3. **String input.** If the first character is `"`, the input is a string
   literal. Return everything up to and including its closing quote (same
   escaping rule as above).
4. **Unterminated containers.** If a bracketed value never returns to depth 0
   (including the case where the input ends inside a string literal), return
   the whole input unchanged.
5. All other characters (digits, letters, `,`, `:`, whitespace, ...) are copied
   through untouched and have no effect on the scan.
6. The result is always a prefix (a substring starting at index 0) of the input.
   The function is pure and safe for concurrent use.

## 3. Input specification

- `json`: a non-empty Go string (arbitrary bytes, usually UTF-8). Its first
  byte is usually `[`, `{`, `(` or `"`, but may be any byte (rule 1).
- When the first byte is `"`, the string literal is always terminated in the
  input (an unterminated leading string literal is never passed).

## 4. Output specification

- A `string`: the prefix of `json` holding the first value, as described above.
- Multi-byte UTF-8 characters never affect the scan (all structural characters
  are ASCII).

## 5. Edge cases and constraints

| input | result |
|---|---|
| `[]` | `[]` |
| `{}` | `{}` |
| `()` | `()` |
| `""` | `""` |
| `{"a":[1,{"b":2}]},3` | `{"a":[1,{"b":2}]}` |
| `{"a":"]"}tail` | `{"a":"]"}` |
| `[("]")]x` | `[("]")]` |
| `(a(b)c) d` | `(a(b)c)` |
| `[}` | `[}` |
| `[[[]]]]]` | `[[[]]]` |
| `[1]   [2]` | `[1]` |
| `[1,2` | `[1,2` (never closed) |
| `["unterminated` | `["unterminated` |
| `"a\"b"x` | `"a\"b"` (escaped quote does not end the string) |
| `"a\\"b` | `"a\\"` (two backslashes: the quote closes the string) |
| `"\\\""tail` | `"\\\""` |
| `["\\"]x` | `["\\"]` |
| `{"a":"\"}"}rest` | `{"a":"\"}"}` |
| `"]"` | `"]"` |
| `a,b}|c` | `a,b}` (first character counts as the opener) |
| `x.#(a|b)}|c` | `x.#(a|b)}` |
| `a]` | `a]` |
| `ab` | `ab` (never closed) |

- Whitespace and newlines inside the value are kept as they are.
- The function never modifies its input and must run in time linear in the
  length of the returned prefix.
