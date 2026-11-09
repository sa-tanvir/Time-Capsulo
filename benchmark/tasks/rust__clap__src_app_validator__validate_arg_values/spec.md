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
