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
