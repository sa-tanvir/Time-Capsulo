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
