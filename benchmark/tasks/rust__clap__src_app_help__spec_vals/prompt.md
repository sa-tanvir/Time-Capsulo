You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Help::spec_vals(&self, a: &ArgWithDisplay) -> String`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). When clap prints an argument's
entry in a help screen, it appends a suffix of "special values" after the help text,
for example

```
-c, --cafe <FILE>    A coffeehouse, coffee shop, or café. [env: ENVVAR=MYVAL]
-p, --pos <VAL>      Some vals [possible values: fast, slow]
    --arg <argument>    Pass an argument to the program. [default: default-argument]
```

`spec_vals` builds that suffix for one argument and returns it as a `String`. It writes
nothing to the stream. The help-output tests compare whole help screens, so the exact
text, spacing and order matter.

## 2. Functional requirements

Build a list of up to four bracketed parts, in this fixed order, each **starting with a
single space**:

1. **Environment variable** — if `a.env()` is `Some((name, value))`:
   - `" [env: NAME=VALUE]"` where `NAME` is the variable name and `VALUE` its value,
     both converted with lossy UTF-8 conversion (`to_string_lossy`). If the variable
     had no value (`value` is `None`) the part is `" [env: NAME=]"`.
   - If the argument has `ArgSettings::HideEnvValues`, the value and the `=` are
     omitted: `" [env: NAME]"`.
2. **Default value** — unless the argument has `ArgSettings::HideDefaultValue`, if
   `a.default_val()` is `Some(v)`: `" [default: V]"` (lossy UTF-8 of `v`).
3. **Aliases** — if `a.aliases()` is `Some(list)` (visible aliases only):
   `" [aliases: a1, a2, a3]"`, the aliases in their given order joined by `", "`.
4. **Possible values** — unless the writer hides possible values globally
   (`self.hide_pv`) or the argument has `ArgSettings::HidePossibleValues`, if
   `a.possible_vals()` is `Some(list)`: `" [possible values: v1, v2]"`, joined by `", "`
   in the given order.

The result is the parts **joined with a single space**. Because every part already
begins with a space, consecutive parts are separated by two spaces, e.g.
`" [env: E=V]  [default: dflt]  [aliases: a1, a2]  [possible values: p1, p2, p3]"`.
If no part applies, the result is the empty string.

**Colour.** When `self.color` is true, the default value, each alias and each possible
value are rendered through `self.cizer.good(...)` (the "good" style) instead of plain
text; brackets, labels, separators and the environment part are never styled. With
colours off the output is plain text exactly as above.

Examples (colour off):

| env | default | visible aliases | possible values | settings / writer | result |
|---|---|---|---|---|---|
| – | – | – | `fast`, `slow` | – | `" [possible values: fast, slow]"` |
| `ENVVAR` (unset) | – | – | – | – | `" [env: ENVVAR=]"` |
| `ENVVAR`=`MYVAL` | – | – | – | – | `" [env: ENVVAR=MYVAL]"` |
| `ENVVAR`=`MYVAL` | – | – | – | HideEnvValues | `" [env: ENVVAR]"` |
| – | `default-argument` | – | – | – | `" [default: default-argument]"` |
| – | `default-argument` | – | – | HideDefaultValue | `""` |
| – | – | `als2`, `als3` | – | – | `" [aliases: als2, als3]"` |
| – | – | – | `vi`, `emacs` | HidePossibleValues, or writer `hide_pv` | `""` |

## 3. Input specification

- `self`: the help writer; only `hide_pv`, `color` and `cizer` are read (see the
  "Instance state" section of the context).
- `a`: any argument (flag, option or positional) accessed through the `AnyArg` trait.
  OS strings may contain non-UTF-8 bytes (replaced by U+FFFD by the lossy conversion).
  Lists may be long (thousands of entries) and contain any Unicode text.

## 4. Output specification

- Returns a newly allocated `String` (possibly empty). Does not write to
  `self.writer` and does not modify `self` or `a`.

## 5. Edge cases and constraints

- An empty-string value of a set environment variable gives `" [env: NAME=]"`, the
  same as an unset one.
- `HideDefaultValue` and `HidePossibleValues` suppress only their own part;
  `HideEnvValues` hides only the value, never the variable name.
- Hidden aliases are already filtered out by `a.aliases()`; when no visible alias
  exists it returns `None` and no aliases part is produced.
- An empty possible-values slice still produces `" [possible values: ]"`.
- Order of parts is always env, default, aliases, possible values.
- Linear in the total length of the produced text.

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
fn spec_vals(&self, a: &ArgWithDisplay) -> String {
    // TODO: implement according to the specification
}
```
