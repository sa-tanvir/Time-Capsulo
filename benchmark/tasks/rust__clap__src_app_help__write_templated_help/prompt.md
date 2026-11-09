You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Help::write_templated_help(&mut self, parser: &Parser, template: &str) -> ClapResult<()>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). An application may replace the
default help layout with a **template** (`App::template`), a text containing tags in
curly braces, e.g.

```
{bin} {version}
{author}
{about}

USAGE:
    {usage}

{all-args}
```

This method writes the template to `self.writer`, copying ordinary text verbatim and
replacing every recognised tag by the corresponding piece of help. The template tests
compare complete help screens, and malformed or unknown tags must be reproduced exactly
as specified below.

## 2. Functional requirements

### 2.1 Scanning

Process the template's **bytes** from left to right:

1. Copy bytes to the output until a `{` is found (the `{` itself is not copied yet).
   If the template ends first, stop.
2. After a `{`, look at **at most the next 15 bytes** for a closing `}`:
   - `}` found at offset `k` (`0 <= k <= 14`): the `k` bytes between the braces are the
     **tag**; both braces and the tag are consumed. Then:
     - `k == 0` (an empty `{}`): write nothing and continue scanning.
     - otherwise handle the tag (2.2) and continue scanning after the `}`.
   - No `}` within those bytes, but at least one byte was read: write `{` followed by
     the bytes that were read (up to 15, verbatim — a `{` among them does **not** start
     a new tag), then continue scanning normally after them.
   - The template ends immediately after the `{`: write nothing more and stop (a
     trailing `{` is dropped).
3. Text outside tags, including a lone `}`, is copied unchanged.

### 2.2 Tags (exact, case-sensitive, no whitespace)

| tag | output |
|---|---|
| `bin` | the binary name, via `self.write_bin_name(parser)` |
| `version` | `parser.meta.version`, or `unknown version` |
| `author` | `parser.meta.author`, or `unknown author` |
| `about` | `parser.meta.about`, or `unknown about` |
| `long-about` | `parser.meta.long_about`, or `unknown about` |
| `usage` | `usage::create_usage_no_title(parser, &[])` |
| `all-args` | `self.write_all_args(parser)` (all sections with headers) |
| `unified` | `self.write_args` over all flags followed by all options |
| `flags` | `self.write_args` over the flags |
| `options` | `self.write_args` over the options |
| `positionals` | `self.write_args` over the positionals |
| `subcommands` | `self.write_subcommands(parser)` |
| `after-help` | `parser.meta.more_help`, or `unknown after-help` |
| `before-help` | `parser.meta.pre_help`, or `unknown before-help` |
| `?` | the text `Could not decode tag name` |
| anything else | written back unchanged: `{`, the tag bytes, `}` |

### 2.3 Result

Return `Ok(())` when the template is exhausted. Any I/O error (or an error returned by a
section writer) is returned immediately, converted to the crate's `Error`.

### Examples (app `MyApp`, version `1.0`, no author/about)

| template | output |
|---|---|
| `""` | `""` |
| `test no tag test` | `test no tag test` |
| `test {unknown_tag} test` | `test {unknown_tag} test` |
| `a{bin}b{version}` | `aMyAppb1.0` |
| `{author}/{about}/{after-help}` | `unknown author/unknown about/unknown after-help` |
| `{?}` | `Could not decode tag name` |
| `{}` | `""` |
| `x{` | `x` |
| `{bin` | `{bin` |
| `}{bin}{` | `}MyApp` |
| `{{bin}}` | `{{bin}}` (tag is `{bin`, unknown) |
| `{ bin }` | `{ bin }` |
| `{BIN}` | `{BIN}` |
| `{this-tag-is-way-too-long} after` | unchanged (no `}` within 15 bytes) |
| `{nope lorem ipsum {bin}` | `{nope lorem ipsu` + `m ` + `MyApp`, i.e. `{nope lorem ipsum MyApp` |

## 3. Input specification

- `self`: the help writer (see "Instance state"); section tags use its width/colour
  settings through the sibling writers.
- `parser`: a fully built `Parser` (meta data and arguments).
- `template`: arbitrary UTF-8 text, possibly empty or very long; braces need not be
  balanced.

## 4. Output specification

- Writes the expanded template to `self.writer`; returns `ClapResult<()>`.
- Ordinary text is reproduced byte-for-byte (including multi-byte characters; the
  15-byte window counts bytes).

## 5. Edge cases and constraints

- The longest tag that can be recognised is 14 bytes; all valid tag names are shorter.
- Repeated tags are expanded each time.
- Must not modify `parser`; must work in a single left-to-right pass (cost linear in the
  template length plus the cost of the expanded sections).

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
write_args & mut self , args : I
write_args_unsorted & mut self , args : I
write_before_after_help & mut self , h : & str
write_bin_name & mut self , parser : & Parser
write_default_help & mut self , parser : & Parser
write_help & mut self , parser : & Parser
write_parser_help w : & a mut Write , parser : & Parser , use_long : bool
write_parser_help_to_stderr w : & a mut Write , parser : & Parser
write_subcommands & mut self , parser : & Parser
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

## Sibling methods / helpers used by templates (already implemented)

- `fn write_bin_name(&mut self, parser: &Parser) -> io::Result<()>` — writes the binary name (`{bin}`).
- `pub fn write_all_args(&mut self, parser: &Parser) -> ClapResult<()>` — all sections with headers (`{all-args}`).
- `fn write_args<…>(&mut self, args: I) -> io::Result<()>` where `I: Iterator<Item = &ArgWithOrder>` — entries of
  the given arguments, sorted, without header.
- `fn write_subcommands(&mut self, parser: &Parser) -> io::Result<()>` — subcommand entries without header.
- `as_arg_trait(x)` — converts `&FlagBuilder`/`&OptBuilder`/`&PosBuilder` into `&ArgWithOrder`
  (`parser.flags().map(as_arg_trait)`).
- `usage::create_usage_no_title(parser: &Parser, used: &[&str]) -> String` — the usage line without `USAGE:`.
- `copy_until(r, w, delimiter_byte) -> CopyUntilResult` and `copy_and_capture(r, w, tag_buffer) -> Option<io::Result<usize>>`
  are file-local helpers you may use (see their doc comments in the file); `CopyUntilResult` has variants
  `DelimiterFound(usize)`, `DelimiterNotFound(usize)`, `ReaderEmpty`, `ReadError(io::Error)`, `WriteError(io::Error)`.

## `Parser` members used here

- `parser.meta: AppMeta` with `version`, `author`, `about`, `long_about`, `more_help` (after-help text),
  `pre_help` (before-help text): all `Option<&str>`.
- `parser.flags()`, `parser.opts()`, `parser.positionals()` — iterators over the app's arguments.
- `io::Error` converts into the crate error with `?` / `Error::from`.

=== STUB ===
```rust
fn write_templated_help(&mut self, parser: &Parser, template: &str) -> ClapResult<()> {
    // TODO: implement according to the specification
}
```
