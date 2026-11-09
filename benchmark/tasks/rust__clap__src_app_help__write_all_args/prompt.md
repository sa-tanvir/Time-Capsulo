You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Help::write_all_args(&mut self, parser: &Parser) -> ClapResult<()>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). It writes the argument sections of
a help screen: the `FLAGS:`, `OPTIONS:`, `ARGS:` and `SUBCOMMANDS:` blocks that follow
the `USAGE:` line, e.g.

```
FLAGS:
    -h, --help       Prints help information
    -V, --version    Prints version information

OPTIONS:
    -o, --option <opt>    tests options

ARGS:
    <positional>    tests positionals

SUBCOMMANDS:
    help      Prints this message or the help of the given subcommand(s)
    subcmd    tests subcommands
```

It decides which sections exist, in what order, with which header, and how they are
separated; the entries themselves are produced by the sibling section writers listed in
the context. The help-output tests compare whole help screens.

## 2. Functional requirements

1. **Which sections exist.**
   - flags: `parser.has_flags()`; options: `parser.has_opts()` (both true even if every
     element is hidden);
   - positionals: at least one positional **without** `ArgSettings::Hidden`;
   - subcommands: `parser.has_visible_subcommands()`.
2. **Unified mode.** If the parser has `AppSettings::UnifiedHelpMessage` **and** there
   are flags or options, write a single section with header `OPTIONS:\n` whose entries
   are all flags followed by all options, passed together (flags first, then options,
   as one iterator) to `self.write_args` (which sorts them).
3. **Normal mode** (otherwise):
   - if there are flags: header `FLAGS:\n`, then `write_args` over the flags;
   - if there are options: header `OPTIONS:\n`, then `write_args` over the options.
4. **Positionals** (both modes): header `ARGS:\n`, then `write_args_unsorted` over all
   positionals (in index order; the writer itself skips hidden ones).
5. **Subcommands**: header `SUBCOMMANDS:\n`, then `write_subcommands(parser)`.
6. **Order and separation.** Sections appear in the order flags, options (or the unified
   options section), args, subcommands. Before every section except the first one
   written, write `"\n\n"`. Nothing is written before the first header or after the last
   entry (no trailing newline). If no section exists, nothing is written at all.
7. **Headers** are written in the "warning" colour style (`color!(self, "…", warning)`;
   plain text when colours are off). Separators are written plain.
8. Errors from writing are converted to the crate error type and returned immediately;
   on success return `Ok(())`.

Example: an app with only positionals `<a>` and `<b>` (help "first"/"second") writes

```
ARGS:
    <a>    first
    <b>    second
```

An app with UnifiedHelpMessage, flag `-f` and option `--opt <x>` writes a single
`OPTIONS:` section containing both entries; without the setting it writes `FLAGS:`
(with `-f`), a blank line, then `OPTIONS:` (with `--opt`). A subcommand named `help`
alone does not create a `SUBCOMMANDS:` section; if other visible subcommands exist, the
section lists all non-hidden subcommands including `help`.

## 3. Input specification

- `self`: the help writer (see "Instance state"); the section writers update
  `self.longest` and `self.force_next_line` themselves.
- `parser`: a fully built `Parser` (flags, options, positionals, subcommands, settings).

## 4. Output specification

- Writes the sections to `self.writer`; returns `ClapResult<()>`.

## 5. Edge cases and constraints

- If every positional is hidden, no `ARGS:` section is written (not even a header).
- If all flags (or options) are hidden, the header is still written, followed by no
  entries.
- In unified mode with no flags and no options, no `OPTIONS:` section is written, but
  `ARGS:`/`SUBCOMMANDS:` still follow the normal rules (the first written section has no
  leading `"\n\n"`).
- Does not change parser state.

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

## Sibling methods of `Help` used for the sections (already implemented)

- `fn write_args<'b: 'd, 'c: 'd, 'd, I: 'd>(&mut self, args: I) -> io::Result<()> where I: Iterator<Item = &'d ArgWithOrder<'b, 'c>>`
  — writes one entry per visible argument, sorted by display order then name, entries separated by `"\n"`
  (no trailing newline); computes `self.longest` itself.
- `fn write_args_unsorted<…>(&mut self, args: I) -> io::Result<()>` — same, but keeps the given order.
- `fn write_subcommands(&mut self, parser: &Parser) -> io::Result<()>` — writes one entry per non-hidden
  subcommand (sorted by display order then name), separated by `"\n"`.
- free function `as_arg_trait<'a, 'b, T: ArgWithOrder<'a, 'b>>(x: &T) -> &ArgWithOrder<'a, 'b>` — converts a
  `&FlagBuilder` / `&OptBuilder` / `&PosBuilder` into the trait object these methods take (e.g.
  `parser.flags().map(as_arg_trait)`).

## `Parser` (`src/app/parser.rs`) members used here

- `parser.has_flags() -> bool`, `parser.has_opts() -> bool` — at least one flag / option exists (hidden ones count).
- `parser.flags()` / `parser.opts()` — iterators over `&FlagBuilder` / `&OptBuilder` in declaration order.
- `parser.positionals()` — iterator over `&PosBuilder` in index order.
- `parser.has_visible_subcommands() -> bool` — some subcommand other than one named `help` is not hidden.
- `parser.is_set(AppSettings::UnifiedHelpMessage) -> bool`.
- Errors: `io::Error` converts into the crate error with `?` / `Error::from` (`ClapResult<T>` = `Result<T, clap::Error>`).

=== STUB ===
```rust
pub fn write_all_args(&mut self, parser: &Parser) -> ClapResult<()> {
    // TODO: implement according to the specification
}
```
