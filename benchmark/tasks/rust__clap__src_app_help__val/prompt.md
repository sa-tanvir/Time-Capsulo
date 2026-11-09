You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Help::val(&mut self, arg: &ArgWithDisplay) -> Result<String, io::Error>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). Each argument entry of a help
screen is written in four steps: the short switch, the long switch, then **`val`**, then
the help text. For example in

```
    -o, --option <file> <name>    some help [possible values: a, b]
    <input>...                    the input files
```

`val` writes the **value placeholders** (` <file> <name>`… after the switches; the whole
`<input>...` for a positional), then decides whether the help text must move to the next
line, writes the **padding spaces** that align the help column, and returns the
argument's "special values" suffix (`[default: …]`, `[possible values: …]`, …) for the
next step. The help-output tests compare entire screens, so every character and every
padding space counts.

## 2. Functional requirements

### 2.1 Value placeholders (only if `arg.takes_value()`)

Flags (`takes_value() == false`) write no placeholders. Otherwise, let `delim` be
`arg.val_delim()` if the argument has `ArgSettings::RequireDelimiter`, else a space.
All placeholders below are written in the "good" colour style (via `color!(…, good)`;
plain text when colours are off); delimiters are written plain.

1. If `arg.val_names()` is `Some(names)`: write `<name>` for every name in index order,
   with `delim` between consecutive ones. If the argument has `ArgSettings::Multiple`
   and there is exactly one name, then write `...`.
2. Else if `arg.num_vals()` is `Some(n)`: write `<NAME>` `n` times (`NAME` =
   `arg.name()`), separated by `delim`; if `Multiple` and `n == 1`, write `...`.
3. Else if the argument has a switch (an option): write `<NAME>`, plus `...` if
   `Multiple`.
4. Else (a positional without names or count): write the argument's own `Display`
   text (e.g. `<input>...`), styled "good".

Nothing is written before the placeholders (the separator after the long switch was
already written by the previous step).

### 2.2 Special values and line decision

- `spec = self.spec_vals(arg)` (sibling method; returns e.g. `" [default: x]"` or `""`).
- `h` = `arg.help()` or `""` (always the short help, even in long-help mode);
  `h_w = str_width(h) + str_width(spec)`.
- `nlh = self.next_line_help || arg has ArgSettings::NextLineHelp`.
- `taken = self.longest + 12`.
- Set **`self.force_next_line`** to true exactly when all hold: `!nlh`,
  `self.term_w >= taken`, `taken / term_w > 0.40` (computed as `f32` division), and
  `h_w > term_w - taken`; otherwise set it to false.

### 2.3 Padding (only when `!(nlh || self.force_next_line)`; otherwise write nothing more)

Let `w = str_width(arg.to_string())` (display width of the argument's signature).
- Argument with a switch: write `self.longest - w` spaces plus **4** more if the
  argument has a long name (`arg.long().is_some()`), or plus **8** more if it has only
  a short name.
- Positional: write `self.longest + 4 - w` spaces.

### 2.4 Result

Return `Ok(spec)`. Any I/O error from writing is returned as `Err` immediately.

### Examples (colour off, writer at the position after the switches)

| argument | `longest` | written by `val` | returns |
|---|---|---|---|
| option `--option`/`-o`, name `opt`, no value names, help `"h"` | 14 | `<opt>` + 4 spaces | `""` |
| option `-o` only, value names `file`,`name` | 16 | `<file> <name>` + 8 spaces | `""` |
| option `--fake`/`-f`, names `some`,`val`, RequireDelimiter `:` | 19 | `<some>:<val>` + 4 spaces | `""` |
| option `--opt`, `num_vals = 3`, Multiple, RequireDelimiter `,`, name `o` | 17 | `<o>,<o>,<o>` + 4 spaces | `""` |
| flag `--flag`/`-f`, longest 10 | 10 | 8 spaces (= 10 − 6 + 4) | `""` |
| positional `<input>...`, longest 12, possible values `vi`, `emacs` | 12 | `<input>...` + 6 spaces | `" [possible values: vi, emacs]"` |
| any argument with NextLineHelp | – | placeholders only, no padding | spec |

(`longest` is set by the section writer to the widest signature of the section; for
switches the signature is the `Display` text, e.g. `--option <opt>` has width 14.)

## 3. Input specification

- `self`: the help writer (see the "Instance state" section): reads `next_line_help`,
  `term_w` (may be `usize::MAX` = unlimited), `longest`, `color`/`cizer`, `hide_pv`;
  writes `force_next_line`; writes to `self.writer`.
- `arg`: flag, option or positional; `self.longest >= str_width(arg.to_string())` is
  guaranteed by the callers.
- Names and help text may contain any Unicode; widths are display widths
  (`str_width`), not byte lengths.

## 4. Output specification

- Bytes written to `self.writer` as described; `self.force_next_line` updated (always
  assigned, also for flags and positionals).
- Returns `Ok(String)` containing exactly what `self.spec_vals(arg)` returns.

## 5. Edge cases and constraints

- `...` is written only for a single value slot; two or more names/values never get it.
- `num_vals == Some(0)` writes no placeholders.
- `term_w < taken` never forces the next line; with `term_w == usize::MAX` the ratio
  is effectively 0, so the next line is never forced.
- When `nlh` or `force_next_line` is true, no padding is written (the help step will
  start a new line).
- The placeholders do not depend on `self.use_long`.
- Cost is linear in the number of value slots and the help/spec length.

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
help & mut self , arg : & ArgWithDisplay < b , c > , spec_vals : & str
long & mut self , arg : & ArgWithDisplay < b , c >
new w : & a mut Write , next_line_help : bool , hide_pv : bool , color : bool , cizer : Colorizer , term_w : Option < usize > , max_w : Option < usize > , use_long : bool ,
short & mut self , arg : & ArgWithDisplay < b , c >
spec_vals & self , a : & ArgWithDisplay
str_width s : & str
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
fn val<'b, 'c>(&mut self, arg: &ArgWithDisplay<'b, 'c>) -> Result<String, io::Error> {
    // TODO: implement according to the specification
}
```
