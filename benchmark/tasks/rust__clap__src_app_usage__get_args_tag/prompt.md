You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `usage::get_args_tag(p: &Parser, incl_reqs: bool) -> Option<String>`

## 1. Component overview

Part of `clap` 2.30's usage-string generator (`src/app/usage.rs`). A usage line such as

```
prog [FLAGS] [OPTIONS] <input> [output] [SUBCOMMAND]
```

lists the required positionals explicitly and summarises the **optional** positionals.
`get_args_tag` produces that summary for the optional positionals of parser `p`:

- `None` means "use the generic `[ARGS]` tag" (the caller then writes ` [ARGS]`);
- `Some(text)` is text appended verbatim to the usage line, e.g. `" [output]"`,
  `" [files]..."`, or `""` (nothing).

`incl_reqs` is `true` for the primary usage line (required positionals are printed
separately by the caller) and `false` for the secondary usage string built when
required arguments are listed elsewhere. Many usage, help and error-message tests
depend on this text.

## 2. Functional requirements

Definitions:
- A positional is **eligible** if it is not `Required`, not `Hidden` and not `Last`
  (`ArgSettings`).
- **Rendering** of a positional: `" [" + pos.name_no_brackets() + "]" + pos.multiple_str()`
  (note the leading space), e.g. `" [file]"`, `" [file]..."`, `" [<a> <b>]"`.
- **count** = number of eligible positionals that are *not* members of any **required**
  argument group (`p.groups` entries with `required == true` whose `args` contain the
  positional's name). Members of non-required groups are counted normally.
- `dont_collapse` = `p.is_set(AppSettings::DontCollapseArgsInUsage)`.

Decide in this order (first match wins):

1. `!dont_collapse && count > 1` → `None`.
2. `count == 1 && incl_reqs` → `Some(rendering of the first eligible positional)` in
   index order. "First eligible" ignores group membership: if an earlier eligible
   positional belongs to a required group, that one is rendered.
3. `dont_collapse && p has at least one positional && incl_reqs` → `Some` of the
   renderings of **all** eligible positionals (group membership ignored) concatenated in
   index order (possibly `""`).
4. `!incl_reqs` → let `h` be the largest index of a positional that is `Required` and not
   `Last`, or, if there is none, the number of positionals. Return `Some` of the
   renderings of all eligible positionals with index `<= h`, concatenated in index order
   (possibly `""`).
5. Otherwise → `Some("")`.

Examples (positionals in index order; `R` = required, `M` = multiple, `H` = hidden;
`incl_reqs = true` unless stated):

| positionals | setting | result |
|---|---|---|
| none | – | `Some("")` |
| `a` | – | `Some(" [a]")` |
| `a(R)` | – | `Some("")` |
| `a`, `b` | – | `None` |
| `a`, `b` | DontCollapseArgsInUsage | `Some(" [a] [b]")` |
| `a(R)`, `b(M)` | – | `Some(" [b]...")` |
| `a(M)` with value names `x`,`y` | – | `Some(" [<x> <y>]")` |
| `a(M)` with value name `x` | – | `Some(" [x]...")` |
| `a` in required group, `b` | – | `Some(" [a]")` (count 1, first eligible is `a`) |
| `a`, `b` both in required group | – | `Some("")` |
| `a`, `b(H)` | – | `Some(" [a]")` |
| `a(R)`, `b`, `c(R)`, `d`; `incl_reqs = false` | – | `Some(" [b]")` (index ≤ 3) |
| `a`, `b`; `incl_reqs = false` | DontCollapse off | `None` (rule 1 first) |
| `a`; `incl_reqs = false` | – | `Some(" [a]")` (rule 4, `h` = 1) |

## 3. Input specification

- `p`: a built parser. Positional indices are the keys of `p.positionals` (normally
  `1..=n`). Groups may list names that are not positionals.
- `incl_reqs`: see above.

## 4. Output specification

- `Option<String>` as defined; the function is pure (reads `p` only).

## 5. Edge cases and constraints

- Hidden, Last and Required positionals never appear in the output.
- With `DontCollapseArgsInUsage` and `incl_reqs == true` and no eligible positionals,
  the result is `Some("")`.
- Must handle thousands of positionals and groups; avoid needless allocation per
  positional.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/app/usage.rs`

## Imports / includes available in this file

```
use std::collections::{BTreeMap, VecDeque};
use INTERNAL_ERROR_MSG;
use args::{AnyArg, ArgMatcher, PosBuilder};
use args::settings::ArgSettings;
use app::settings::AppSettings as AS;
use app::parser::Parser;
```

## Other functions defined in the same file (signatures only; you may call them)

```
create_error_usage p : & Parser < a , b > , matcher : & b ArgMatcher < a > , extra : Option < & str > ,
create_help_usage p : & Parser , incl_reqs : bool
create_smart_usage p : & Parser , used : & [ & str ]
create_usage_no_title p : & Parser , used : & [ & str ]
create_usage_with_title p : & Parser , used : & [ & str ]
get_required_usage_from p : & Parser < a , b > , reqs : & [ & a str ] , matcher : Option < & ArgMatcher < a > > , extra : Option < & str > , incl_last : bool ,
needs_flags_tag p : & Parser
```

## Data used by this function

`p: &Parser` (`src/app/parser.rs`):
- `p.positionals: VecMap<PosBuilder>` — positional arguments keyed by their 1-based index; `.values()` yields
  `&PosBuilder` and `.iter()` yields `(usize, &PosBuilder)`, both in ascending index order; `.len()`, `.is_empty()`.
- `p.groups: Vec<ArgGroup>` — each with public fields `name: &str`, `args: Vec<&str>` (member argument names) and
  `required: bool`.
- `p.groups_for_arg(name: &str) -> Option<Vec<&str>>` — names of all groups listing `name` as a member (`None` if none).
- `p.is_set(AS::DontCollapseArgsInUsage) -> bool` (`AS` = `app::settings::AppSettings`).

`PosBuilder` (`src/args/arg_builder/positional.rs`):
- `pos.b.name: &str`, `pos.name() -> &str`; `pos.is_set(ArgSettings::X)` / `pos.b.is_set(ArgSettings::X)`
  for `Required`, `Hidden`, `Last`, `Multiple`.
- `pos.name_no_brackets() -> Cow<str>` — display name without angle brackets: the single value name if exactly one
  is set; if two or more value names are set, each wrapped in `<…>` and joined by the value delimiter (space by
  default), e.g. `<one> <two>`; otherwise the argument's name.
- `pos.multiple_str() -> &str` — `"..."` if the positional is `Multiple` and has fewer than two value names, else `""`.

=== STUB ===
```rust
fn get_args_tag(p: &Parser, incl_reqs: bool) -> Option<String> {
    // TODO: implement according to the specification
}
```
