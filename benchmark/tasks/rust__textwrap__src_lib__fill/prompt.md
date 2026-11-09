You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/lib.rs`
- **Enclosing scope:** `impl<'a, S: WordSplitter> Wrapper<'a, S>`

## Imports / includes available in this file

```
use std::borrow::Cow;
use std::str::CharIndices;
use unicode_width::UnicodeWidthChar;
use unicode_width::UnicodeWidthStr;
pub use indentation::dedent;
pub use indentation::indent;
pub use splitting::{HyphenSplitter, NoHyphenation, WordSplitter};
    use super::*;
    use hyphenation::{Language, Load, Standard};
        use std::borrow::Cow::{Borrowed, Owned};
```

## Other functions defined in the same file (signatures only; you may call them)

```
auto_hyphenation
auto_hyphenation_with_hyphen
borrowed_lines
break_words
break_words self , setting : bool
break_words_line_breaks
break_words_wide_characters
break_words_zero_width
create_result_line & self , wrapper : & Wrapper < a , S >
empty_input_not_indented
extra_whitespace_start_of_line
fill s : & str , width : usize
fill_simple
forced_split
hyphens
hyphens_alphanumeric
hyphens_flag
hyphens_non_alphanumeric
indent_break_words
indent_multiple_lines
indent_single_line
initial_indent self , indent : & a str
interior_whitespace
into_wrap_iter self , s : & a str
is_whitespace ch : char
issue_129
issue_99
leading_whitespace
long_word
long_words
max_width
multi_word_on_line
multiple_hyphens
multiple_splits
new width : usize
new wrapper : & Wrapper < a , S > , s : & a str
next & mut self
next & mut self , wrapper : & Wrapper < a , S >
no_hyphenation
no_wrap
non_breaking_hyphen
non_breaking_space
preserve_line_breaks
repeated_hyphens
simple
split_len_hyphenation
subsequent_indent self , indent : & a str
termwidth
trailing_hyphen
trailing_whitespace
wide_character_handling
with_splitter width : usize , splitter : S
with_termwidth
wrap & self , s : & a str
wrap s : & str , width : usize
wrap_iter & w self , s : & a str
wrap_iter s : & str , width : usize
wrap_preserve_line_breaks
```

(Signatures above are as extracted by the harness; lifetime parameters such as `'a` appear as `a`.)

## Instance state

`fill` is a method of `impl<'a, S: WordSplitter> Wrapper<'a, S>`. The struct (all fields public):

```rust
pub struct Wrapper<'a, S: WordSplitter> {
    pub width: usize,               // wrap width in display columns
    pub initial_indent: &'a str,    // prepended to the first output line
    pub subsequent_indent: &'a str, // prepended to every following output line
    pub break_words: bool,          // may words longer than `width` be broken
    pub splitter: S,                // word splitter used for hyphenation (default HyphenSplitter)
}
```

Sibling methods on the same impl (public, may be called):

- `pub fn wrap_iter<'w>(&'w self, s: &'a str) -> WrapIter<'w, 'a, S>` - lazy iterator
  (`Iterator<Item = Cow<'a, str>>`) over the wrapped lines of `s`, applying all settings above.
- `pub fn wrap(&self, s: &'a str) -> Vec<Cow<'a, str>>` - the same lines collected into a vector.
- `pub fn into_wrap_iter(self, s: &'a str) -> IntoWrapIter<'a, S>` - consuming variant.
- Builders `new(width)`, `with_splitter(width, splitter)`, `initial_indent(..)`,
  `subsequent_indent(..)`, `break_words(..)`.

=== STUB ===
```rust
pub fn fill(&self, s: &str) -> String {
    // TODO: implement according to the specification
}
```
