You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Help::write_args(&mut self, args: I) -> io::Result<()>`

where `I: Iterator<Item = &'d ArgWithOrder<'b, 'c>>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). It writes the body of one help
section (the lines under `FLAGS:`, `OPTIONS:`, …) for a sequence of arguments:

```
    -d               Turn debugging information on
    -h, --help       Prints help information
    -V, --version    Prints version information
```

It decides which arguments are shown, computes the alignment width shared by the
section, orders the entries and writes them one per line using the sibling `write_arg`.
Most help-output tests depend on its ordering and alignment.

## 2. Functional requirements

1. **Visibility filter.** An argument is shown if it is **not** `Hidden`, or if it has
   `NextLineHelp` (a hidden argument with `NextLineHelp` is still shown). All other
   arguments are ignored completely.
2. **Column width.** Set `self.longest` to `max(2, w₁, w₂, …)` where `wᵢ` is the display
   width (`str_width`) of the signature (`to_string()`) of every *shown* argument whose
   `longest_filter()` is true. (2 is the width of the shortest legal switch `-x`.)
   `self.longest` is reset at the start, so earlier values do not matter, and it keeps
   the computed value after the call.
3. **Order.** Entries are ordered by `disp_ord()` ascending, and among equal display
   orders by `name()` in ascending (byte-wise string) order. If two shown arguments had
   the same display order and the same name, only the last one given would be written
   (names are unique in practice).
4. **Writing.** Write each shown argument with `self.write_arg(arg.as_base())`, in the
   order above, writing a single `"\n"` **between** consecutive entries (none before the
   first or after the last). With no shown arguments nothing is written.
5. Return `Ok(())`; propagate the first I/O error.

Example: flags `-d` (help "Turn debugging information on"), `--help`/`-h`,
`--version`/`-V`, all with default display order 999. Widths counted: `--help` (6) and
`--version` (9); `-d` has no long switch so it does not count; `longest = 9`. Sorted by
name: `debug`, `help`, `version`, producing the three lines shown in §1 joined by `"\n"`.

With display orders `b`→0, `a`→999, `c`→0, the order is `b`, `c`, `a`.

## 3. Input specification

- `self`: the help writer (see "Instance state"); `write_arg` reads `longest`,
  `term_w`, `next_line_help`, etc.
- `args`: any iterator over flags, options and/or positionals (e.g. flags chained with
  options for a unified section). It is consumed once.

## 4. Output specification

- Entries written to `self.writer`; `self.longest` updated as described;
  returns `io::Result<()>`.

## 5. Edge cases and constraints

- Hidden arguments without `NextLineHelp` neither appear nor influence `longest`.
- Flags with only a short switch appear but never widen the column.
- An empty iterator (or all hidden) writes nothing and leaves `longest = 2`.
- Must scale to thousands of arguments (sorting cost `O(n log n)`).

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
val & mut self , arg : & ArgWithDisplay < b , c >
wrap_help help : & str , avail_chars : usize
wrap_help_last_word
write_all_args & mut self , parser : & Parser
write_app_help w : & a mut Write , app : & App , use_long : bool
write_arg & mut self , arg : & ArgWithDisplay < b , c >
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

## Traits and siblings used by this method

- `trait ArgWithOrder<'b, 'c>: ArgWithDisplay<'b, 'c> + DispOrder` with `fn as_base(&self) -> &ArgWithDisplay<'b, 'c>`;
  `DispOrder::disp_ord(&self) -> usize` is the argument's display order (999 by default for flags/options,
  the index for positionals).
- `AnyArg::longest_filter(&self) -> bool` — whether the argument's signature width counts toward the column
  width (false for flags that have only a short switch, true otherwise).
- `fn write_arg<'b, 'c>(&mut self, arg: &ArgWithDisplay<'b, 'c>) -> io::Result<()>` — writes one complete entry
  (short, long, value placeholders + padding, help text), using `self.longest`; it writes no newline after the entry
  (except inside next-line help).
- `VecMap` (`map::VecMap`) and `BTreeMap` are available.

=== STUB ===
```rust
fn write_args<'b: 'd, 'c: 'd, 'd, I: 'd>(&mut self, args: I) -> io::Result<()>
where
    I: Iterator<Item = &'d ArgWithOrder<'b, 'c>>,
{
    // TODO: implement according to the specification
}
```
