You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Help::help(&mut self, arg: &ArgWithDisplay, spec_vals: &str) -> io::Result<()>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). Each argument entry of a help
screen is written as: short switch, long switch, value placeholders + padding (which
also decides `self.force_next_line`), and finally **the help text**, written by this
method. It chooses short or long help, appends the special-values suffix, wraps the
text to the terminal width when needed, and indents continuation lines so they line up
under the help column. Example (terminal width 120, `longest` = 14):

```
    -o, --option <opt>    first line
                          second line
```

or, in "next line" mode:

```
    -o, --option <opt>
            first line
            second line
```

The help-output tests compare whole screens (including the `{n}` line-break marker,
wrapping at the terminal width and long-help mode), so the exact layout matters.

## 2. Functional requirements

1. **Text selection.** If `self.use_long`: `h = arg.long_help()`, falling back to
   `arg.help()`, then `""`. Otherwise: `h = arg.help()`, falling back to
   `arg.long_help()`, then `""`. The text to print is `help = h + spec_vals`.
2. **Mode.** `nlh = self.next_line_help || arg has ArgSettings::NextLineHelp ||
   self.use_long`. The entry is in *next-line mode* when `nlh || self.force_next_line`.
3. **Indent width.** `spcs = 12` in next-line mode, else `self.longest + 12`.
4. **Too long?** `too_long = spcs + str_width(h) + str_width(spec_vals) >= self.term_w`.
5. **Line start.** In next-line mode, first write `"\n"` followed by 12 spaces (three
   `TAB`s).
6. **Wrapping.** If `(too_long && spcs <= self.term_w)` **or** `h` contains the marker
   `{n}`: replace every `{n}` in `help` by `"\n"` and wrap the result with
   `wrap_help(text, self.term_w - spcs)` (wraps each existing line separately to that
   many columns, without breaking words). Otherwise `help` is used unchanged (a `{n}` in
   `spec_vals` alone does not trigger wrapping or replacement).
7. **Writing lines.** Split `help` into lines (`str::lines` semantics: split at `\n`,
   a trailing newline does not create an empty last line, an empty text has no lines).
   Write the first line as-is. For every further line write `"\n"`, then the indent,
   then the line, where the indent is:
   - 12 spaces in next-line mode;
   - otherwise `self.longest + 12` spaces if the argument has a switch
     (`arg.has_switch()`), or `self.longest + 8` spaces for a positional.
8. **Trailing newline.** If, after wrapping, `help` contains no `'\n'` and the entry is
   in next-line mode, write a final `"\n"`.
9. Return `Ok(())`; propagate write errors immediately.

Examples (`term_w` = 120, no colour, `longest` = 14, option argument):

| help | spec_vals | mode | written |
|---|---|---|---|
| `"some help"` | `""` | normal | `some help` |
| `"line one{n}line two"` | `""` | normal | `line one` `\n` + 26 spaces + `line two` |
| same, positional | `""` | normal | `line one` `\n` + 22 spaces + `line two` |
| `"Some vals"` | `" [possible values: fast, slow]"` | normal | `Some vals [possible values: fast, slow]` |
| `"prints help"` | `""` | next-line (`next_line_help`) | `\n` + 12 spaces + `prints help` + `\n` |
| `"has{n}break"` | `""` | next-line | `\n` + 12 sp + `has` + `\n` + 12 sp + `break` |
| none | `""` | normal | nothing |
| none | `""` | next-line | `\n` + 12 spaces + `\n` |

With `term_w = 60`, `longest = 20`, a 40-word help is wrapped to `60 - 32 = 28`
columns and every continuation line is indented by 32 spaces.

## 3. Input specification

- `self`: the help writer (see "Instance state"): reads `use_long`, `next_line_help`,
  `force_next_line`, `longest`, `term_w` (may be `usize::MAX` = unlimited); writes to
  `self.writer`. Does not modify any field.
- `arg`: a flag, option, positional or subcommand entry (via `AnyArg`).
- `spec_vals`: suffix produced by `spec_vals` (empty or starting with a space).
- Texts may contain any Unicode and real newlines; widths are display widths.

## 4. Output specification

- Writes the help text as described to `self.writer`; returns `io::Result<()>`.

## 5. Edge cases and constraints

- Real `"\n"` characters in the help are always honoured as line breaks (every line is
  re-indented), even when no wrapping happens.
- When `spcs > term_w` the text is not wrapped because of its length (only a `{n}`
  marker triggers wrapping then); callers never combine `{n}` with `spcs > term_w`.
- With `term_w == usize::MAX` text is never too long; only `{n}` triggers wrapping.
- In long-help mode (`use_long`) the entry is always in next-line mode.
- Cost should be linear in the help length (plus the wrapping).

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/app/help.rs`
- **Enclosing scope:** `impl<'a> Help<'a>`

## Imports / includes available in this file

```
use std::borrow::Cow;
use std::cmp;
use std::collections::BTreeMap;
use std::fmt::Display;
use std::io::{self, Cursor, Read, Write};
use std::usize;
use app::{App, AppSettings};
use app::parser::Parser;
use args::{AnyArg, ArgSettings, DispOrder};
use errors::{Error, Result as ClapResult};
use fmt::{Colorizer, ColorizerOption, Format};
use app::usage;
use map::VecMap;
use INTERNAL_ERROR_MSG;
use unicode_width::UnicodeWidthStr;
use term_size;
use textwrap;
    use self::CopyUntilResult::*;
    use super::wrap_help;
```

## Other functions defined in the same file (signatures only; you may call them)

```
_write_parser_help w : & a mut Write , parser : & Parser , stderr : bool , use_long : bool ,
as_arg_trait x : & T
as_base & self
copy_and_capture r : & mut R , w : & mut W , tag_buffer : & mut Cursor < Vec < u8 > > ,
copy_until r : & mut R , w : & mut W , delimiter_byte : u8
dimensions
disp_ord & self
long & mut self , arg : & ArgWithDisplay < b , c >
new w : & a mut Write , next_line_help : bool , hide_pv : bool , color : bool , cizer : Colorizer , term_w : Option < usize > , max_w : Option < usize > , use_long : bool ,
short & mut self , arg : & ArgWithDisplay < b , c >
spec_vals & self , a : & ArgWithDisplay
str_width s : & str
val & mut self , arg : & ArgWithDisplay < b , c >
wrap_help help : & str , avail_chars : usize
wrap_help_last_word
write_all_args & mut self , parser : & Parser
write_app_help w : & a mut Write , app : & App , use_long : bool
write_arg & mut self , arg : & ArgWithDisplay < b , c >
write_args & mut self , args : I
write_args_unsorted & mut self , args : I
write_before_after_help & mut self , h : & str
write_bin_name & mut self , parser : & Parser
write_default_help & mut self , parser : & Parser
write_help & mut self , parser : & Parser
write_parser_help w : & a mut Write , parser : & Parser , use_long : bool
write_parser_help_to_stderr w : & a mut Write , parser : & Parser
write_subcommands & mut self , parser : & Parser
write_templated_help & mut self , parser : & Parser , template : & str
write_version & mut self , parser : & Parser
```

## Instance state (`self: Help<'a>`, the help writer)

| field | type | meaning |
|---|---|---|
| `writer` | `&'a mut Write` | destination stream; write with `write!(self.writer, ...)` / `self.writer.write_all(...)` |
| `next_line_help` | `bool` | app-wide `NextLineHelp`: put every argument's help text on its own line |
| `hide_pv` | `bool` | app-wide `HidePossibleValues`: never list possible values |
| `term_w` | `usize` | usable terminal width in columns (already resolved; `usize::MAX` means "no limit") |
| `color` | `bool` | whether output is colourised |
| `cizer` | `Colorizer` | styling helper: `self.cizer.good(x)` / `.warning(x)` / `.error(x)` return a `Format<T>` that implements `Display` (plain text when colours are off) |
| `longest` | `usize` | display width of the longest argument signature in the current section (set by the section writers) |
| `force_next_line` | `bool` | set per argument: its help must go on the next line because it would not fit |
| `use_long` | `bool` | rendering `--help` (long help) instead of `-h` |

Helpers available in this file / crate:
- `str_width(s: &str) -> usize`: display width (Unicode columns) of `s`.
- `const TAB: &str = "    "` (4 spaces).
- macro `color!(self, "<fmt>", value, good)` (or `color!(self, value, good)`): writes `value` to `self.writer`,
  styled with `self.cizer.good` if `self.color`, plain otherwise; evaluates to `io::Result<()>`.
- macro `write_nspaces!(self.writer, n)`: writes `n` spaces (uses `?`, so only inside functions returning `io::Result`).
- `wrap_help(help: &str, avail_chars: usize) -> String`: wraps text to the given width (textwrap), keeping
  existing newlines.
- `INTERNAL_ERROR_MSG: &str` — message for "cannot happen" panics.

## Arguments: `ArgWithDisplay` / `AnyArg`

`arg: &ArgWithDisplay` is any clap argument (flag, option, positional) that implements `Display` (its signature,
e.g. `--config <FILE>`, `-v`, `<input>...`) and the `AnyArg` accessor trait (`src/args/any_arg.rs`):
`name() -> &str`, `short() -> Option<char>`, `long() -> Option<&str>`, `has_switch() -> bool` (false only for
positionals), `takes_value() -> bool`, `is_set(ArgSettings) -> bool`, `val_names() -> Option<&VecMap<&str>>`
(ordered by index), `num_vals() -> Option<u64>`, `val_delim() -> Option<char>`, `help() -> Option<&str>`,
`long_help() -> Option<&str>`, `default_val() -> Option<&OsStr>`, `env() -> Option<(&OsStr, Option<&OsString>)>`
(variable name, and its value if it was set when the argument was defined), `aliases() -> Option<Vec<&str>>`
(visible aliases only; `None` when there are none), `possible_vals() -> Option<&[&str]>`.

=== STUB ===
```rust
fn help<'b, 'c>(&mut self, arg: &ArgWithDisplay<'b, 'c>, spec_vals: &str) -> io::Result<()> {
    // TODO: implement according to the specification
}
```
