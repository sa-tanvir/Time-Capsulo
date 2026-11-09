# Functional specification: `Wrapper::fill(&self, s: &str) -> String`

## 1. Component overview

Part of `textwrap` 0.11, a Rust crate for word wrapping text for terminal output. A `Wrapper`
holds wrapping settings (width, first-line and subsequent-line indentation, whether long words may
be broken, and a word splitter for hyphenation). `fill` is the method that wraps a text and returns
it as **one string** with the wrapped lines separated by newlines. The crate's free function
`textwrap::fill(s, width)` is `Wrapper::new(width).fill(s)`.

## 2. Functional requirements

1. Wrap `s` with this wrapper's settings, producing exactly the sequence of lines yielded by
   `self.wrap_iter(s)` (equivalently, the elements of `self.wrap(s)`); see "Instance state" in the
   context for these methods. The wrapping rules themselves (measuring display width, breaking at
   whitespace, splitting at hyphens, breaking over-long words, keeping existing newlines, adding
   `initial_indent` to the first line and `subsequent_indent` to the others) are entirely those of
   that iterator; `fill` must not change, trim, re-indent or drop any line.
2. Return the lines concatenated in order with a single `\n` **between** consecutive lines. No
   `\n` is added before the first line or after the last line.
3. If the iterator yields no lines (e.g. empty input), return the empty string - in particular no
   indentation is emitted for empty input.

Examples (free function `fill(s, w)` = `Wrapper::new(w).fill(s)`):

| call | result |
|---|---|
| `fill("foo bar baz", 10)` | `"foo bar\nbaz"` |
| `fill("Memory safety without garbage collection.", 15)` | `"Memory safety\nwithout garbage\ncollection."` |
| `fill("test\n", 11)` | `"test\n"` |
| `fill("test\n\na\n\n", 11)` | `"test\n\na\n\n"` |
| `fill("1 3 5 7\n1 3 5 7", 7)` | `"1 3 5 7\n1 3 5 7"` |
| `fill("1 3 5 7\n1 3 5 7", 5)` | `"1 3 5\n7\n1 3 5\n7"` |
| `fill("ab\ncdefghijkl", 5)` | `"ab\ncdefg\nhijkl"` |
| `fill("abcdefgh\nijkl", 5)` | `"abcde\nfgh\nijkl"` |
| `Wrapper::new(10).initial_indent("!!!").fill("")` | `""` |
| `Wrapper::new(10).initial_indent(">>>").fill("foo")` | `">>>foo"` (no space is inserted after the indent) |
| `Wrapper::new(5).break_words(false).fill("foo\u{a0}bar\u{a0}baz")` | unchanged: non-breaking spaces are not break points |
| `Wrapper::new(5).break_words(false).fill("foo\u{2011}bar\u{2011}baz")` | unchanged: non-breaking hyphens are not split points |
| `Wrapper::new(10).initial_indent("* ").subsequent_indent("  ").fill("foo bar baz qux\n\nend\n")` | `"* foo bar\n  baz qux\n  \n  end\n"` |

(Where the input ends with `\n`, the last yielded line itself ends with that newline, which is why
`"test\n"` round-trips; `fill` adds nothing.)

## 3. Input specification

- `&self`: a `Wrapper<'a, S>` with any settings (`width` may be `0` or `usize::max_value()`).
- `s: &str`: any UTF-8 text, possibly empty or multi-line.

## 4. Output specification

- A newly allocated `String` equal to the yielded lines joined with `"\n"`. The wrapper is only
  read, never modified; the call is pure given the wrapper and the splitter.

## 5. Edge cases and constraints

- Empty input returns `""`.
- A single yielded line is returned as-is (no newline appended).
- Lines may themselves contain a trailing `\n` (final line of an input ending in a newline) or
  consist only of an indent; they are copied verbatim.
- Should run in time linear in the input length; avoid unnecessary reallocation (the output is
  typically about as long as `s`).
