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
