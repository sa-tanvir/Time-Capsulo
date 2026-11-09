You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Validator::validate_arg_values(&self, arg: &A, ma: &MatchedArg, matcher: &ArgMatcher) -> ClapResult<()>`

## 1. Component overview

Part of `clap` 2.30's post-parse validation (`src/app/validator.rs`). After the command
line has been parsed, clap checks every value given to each argument. This method checks
the values `ma.vals` of one argument `arg` against the argument's rules — UTF-8
strictness, the list of possible values (optionally case-insensitive), the ban on empty
values, and user-supplied validator closures — and returns the **first** violation as
a clap `Error` (whose kind and message the tests inspect, e.g.
`error: 'faster' isn't a valid value for '--opt <opt>...'`).

## 2. Functional requirements

Examine the values in order. For each value `val`, apply these checks in this order;
the first failing check returns `Err` immediately (later values and checks are not
examined, and validators are not called for them):

1. **Strict UTF-8.** If the app has `AppSettings::StrictUtf8` and `val` is not valid
   UTF-8 → fail with `Error::invalid_utf8` given `usage` and `color` (kind `InvalidUtf8`).
2. **Possible values.** If `arg.possible_vals()` is `Some(pvs)`: let `s` be the lossy
   UTF-8 conversion of `val`. The value is accepted if
   - with `ArgSettings::CaseInsensitive`: some entry equals `s` ignoring **ASCII** case
     only (non-ASCII letters must match exactly);
   - otherwise: some entry equals `s` exactly.
   If not accepted → fail with `Error::invalid_value` given the bad value `s`, the list
   `pvs`, the argument, `usage` and `color` (kind `InvalidValue`; the constructor builds the "did you mean" suggestion and sorted list).
3. **Empty values.** If the argument does **not** have `ArgSettings::EmptyValues`, `val`
   is empty, and `matcher.contains(arg.name())` → fail with `Error::empty_value` given the
   argument, `usage` and `color` (kind `EmptyValue`). If the argument is not recorded in the matcher, empty
   values pass this check.
4. **Validator.** If `arg.validator()` is `Some(f)`: call `f` with the lossy UTF-8
   `String` of `val`; if it returns an error message `msg` → fail with `Error::value_validation`
   given the argument (as `Some`), `msg` and `color` (kind `ValueValidation`).
5. **OS validator.** If `arg.validator_os()` is `Some(f)`: call `f(&val)`; if it returns
   an error `os_msg` → fail the same way as in 4, with the lossy `String` of `os_msg` as
   the message.

If every value passes, return `Ok(())` (also when `ma.vals` is empty).

Here `usage` is the error-usage text produced by `usage::create_error_usage` for this
parser and matcher with no extra argument, and `color` is the parser's colour setting
(`color()`). Build the usage text only when an error is actually returned.

Examples (option `--opt <opt>...`, possible values `fast`, `slow` unless stated):

| values | settings | result |
|---|---|---|
| `fast` | – | `Ok(())` |
| `slow`, `fast`, `slow` | – | `Ok(())` |
| `faster` | – | `Err`, kind `InvalidValue` (bad value `faster`) |
| `FAST` | – | `Err` `InvalidValue` |
| `FAST`, `Slow` | CaseInsensitive | `Ok(())` |
| `""` then `fast` | – | `Err` `InvalidValue` (the empty value is not a possible value) |
| `ok`, `""` (no possible values) | – | `Err` `EmptyValue` |
| `ok`, `""` (no possible values) | EmptyValues | `Ok(())` |
| `good`, `bad` with a validator rejecting `bad` | – | `Err` `ValueValidation` with the validator's message |
| `b"a\xffb"` | StrictUtf8 | `Err` `InvalidUtf8` |
| `b"a\xffb"` (no possible values) | – | `Ok(())` |

## 3. Input specification

- `self.0`: the parser (see "Instance state"); read-only here.
- `arg`: the argument definition (`AnyArg + Display`).
- `ma`: the matched values (`Vec<OsString>`, possibly thousands, possibly empty or
  non-UTF-8).
- `matcher`: the parse result so far.

## 4. Output specification

- `Ok(())` or the first error as described. No other side effects besides calling the
  user validators (in value order, at most once per examined value).

## 5. Edge cases and constraints

- Possible-value matching uses the lossy conversion, so non-UTF-8 input without
  StrictUtf8 is compared as text containing U+FFFD.
- Validators receive owned `String`s (lossy) / `&OsStr`; they are not called for values
  that already failed an earlier check.
- Should stay linear in the number of values times the number of possible values and
  avoid per-value allocation where possible; error construction (usage text) happens
  at most once.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/app/validator.rs`
- **Enclosing scope:** `impl<'a, 'b, 'z> Validator<'a, 'b, 'z>`

## Imports / includes available in this file

```
use std::fmt::Display;
use std::ascii::AsciiExt;
use INTERNAL_ERROR_MSG;
use INVALID_UTF8;
use args::{AnyArg, ArgMatcher, MatchedArg};
use args::settings::ArgSettings;
use errors::{Error, ErrorKind};
use errors::Result as ClapResult;
use osstringext::OsStrExt2;
use app::settings::AppSettings as AS;
use app::parser::{ParseResult, Parser};
use fmt::{Colorizer, ColorizerOption};
use app::usage;
```

## Other functions defined in the same file (signatures only; you may call them)

```
build_err & self , name : & str , matcher : & ArgMatcher
is_missing_required_ok & self , a : & AnyArg , matcher : & ArgMatcher
missing_required_error & self , matcher : & ArgMatcher , extra : Option < & str >
new p : & z mut Parser < a , b >
validate & mut self , needs_val_of : ParseResult < a > , subcmd_name : Option < String > , matcher : & mut ArgMatcher < a > ,
validate_arg_conflicts & self , a : & AnyArg , matcher : & ArgMatcher
validate_arg_num_occurs & self , a : & A , ma : & MatchedArg , matcher : & ArgMatcher ,
validate_arg_num_vals & self , a : & A , ma : & MatchedArg , matcher : & ArgMatcher ,
validate_arg_requires & self , a : & A , ma : & MatchedArg , matcher : & ArgMatcher ,
validate_blacklist & self , matcher : & mut ArgMatcher
validate_matched_args & self , matcher : & mut ArgMatcher < a >
validate_required & mut self , matcher : & ArgMatcher
validate_required_unless & self , a : & AnyArg , matcher : & ArgMatcher
```

## Instance state (`self: &Validator`)

`pub struct Validator<'a, 'b, 'z>(&'z mut Parser<'a, 'b>)` — `self.0` is the parser being validated:
- `self.0.is_set(AS::StrictUtf8) -> bool` (`AS` = `app::settings::AppSettings`): the app rejects non-UTF-8 values.
- `self.0.color() -> ColorWhen`: colour setting to pass to error constructors.

## Other values and helpers

- `ma: &MatchedArg` — `ma.vals: Vec<OsString>`, the values given for the argument in command-line order
  (`ma.occurs: u64` is not needed).
- `matcher: &ArgMatcher` — `matcher.contains(name: &str) -> bool`: whether the argument was matched.
- `arg: &A` (`A: AnyArg + Display`): `name()`, `possible_vals() -> Option<&[&str]>`, `is_set(ArgSettings::X)`
  for `CaseInsensitive` and `EmptyValues`, `validator() -> Option<&Rc<Fn(String) -> Result<(), String>>>`,
  `validator_os() -> Option<&Rc<Fn(&OsStr) -> Result<(), OsString>>>`.
- `OsStrExt2` (imported): `os_str.is_empty_() -> bool`. `AsciiExt` is imported for `eq_ignore_ascii_case` on `str`.
- `usage::create_error_usage(p: &Parser, matcher: &ArgMatcher, extra: Option<&str>) -> String` — the usage text
  embedded in error messages (pass `None` as `extra`).
- Error constructors (`errors::Error`, all return `Error`):
  - `Error::invalid_utf8<U: Display>(usage: U, color: ColorWhen)`
  - `Error::invalid_value<B: AsRef<str>, G: AsRef<str> + Display, U: Display>(bad_val: B, good_vals: &[G], arg: &AnyArg, usage: U, color: ColorWhen)`
  - `Error::empty_value<U: Display>(arg: &AnyArg, usage: U, color: ColorWhen)`
  - `Error::value_validation(arg: Option<&AnyArg>, err: String, color: ColorWhen)`
- `ClapResult<T>` = `Result<T, Error>`.

=== STUB ===
```rust
fn validate_arg_values<A>(
    &self,
    arg: &A,
    ma: &MatchedArg,
    matcher: &ArgMatcher<'a>,
) -> ClapResult<()>
where
    A: AnyArg<'a, 'b> + Display,
{
    // TODO: implement according to the specification
}
```
