# Context for the function to implement

- **Language:** rust
- **File:** `src/args/arg_builder/option.rs`
- **Enclosing scope:** `impl<'n, 'e> Display for OptBuilder<'n, 'e>`

## Imports / includes available in this file

```
use std::fmt::{Display, Formatter, Result};
use std::rc::Rc;
use std::result::Result as StdResult;
use std::ffi::{OsStr, OsString};
use std::mem;
use args::{AnyArg, Arg, ArgSettings, Base, DispOrder, Switched, Valued};
use map::{self, VecMap};
use INTERNAL_ERROR_MSG;
    use args::settings::ArgSettings;
    use super::OptBuilder;
    use map::VecMap;
```

## Other functions defined in the same file (signatures only; you may call them)

```
aliases & self
blacklist & self
default_val & self
default_vals_ifs & self
disp_ord & self
env & s self
eq & self , other : & OptBuilder < n , e >
from a : & z Arg < n , e >
from mut a : Arg < n , e >
has_switch & self
help & self
is_set & self , s : ArgSettings
long & self
long_help & self
longest_filter & self
max_vals & self
min_vals & self
name & self
new name : & n str
num_vals & self
optbuilder_display1
optbuilder_display2
optbuilder_display3
optbuilder_display_multiple_aliases
optbuilder_display_single_alias
overrides & self
possible_vals & self
required_unless & self
requires & self
set & mut self , s : ArgSettings
short & self
takes_value & self
val_delim & self
val_names & self
val_terminator & self
validator & self
validator_os & self
```

## Instance state (`self: &OptBuilder<'n, 'e>`)

`OptBuilder` has three public fields:

- `self.b: Base` — `name: &'n str` (the option's internal name), `settings: ArgFlags`
  (query with `self.b.is_set(ArgSettings::X)` or `self.is_set(ArgSettings::X)`), plus help/relationship
  fields not relevant here.
- `self.s: Switched` — `short: Option<char>`, `long: Option<&'e str>` (no leading dashes),
  `aliases: Option<Vec<(&'e str, bool)>>` (not rendered).
- `self.v: Valued` — `val_names: Option<VecMap<&'e str>>` (from `map::VecMap`: `.iter()` yields
  `(usize, &&str)` in ascending key order, `.len()`, `.values()`), `num_vals: Option<u64>`,
  `val_delim: Option<char>`, plus possible values/defaults/validators (not rendered).

Relevant `ArgSettings` variants: `Multiple`, `RequireEquals`, `RequireDelimiter`.
`INTERNAL_ERROR_MSG: &str` is a crate-level constant for "should never happen" panics.
`Display`, `Formatter` and `Result` (= `std::fmt::Result`) are imported from `std::fmt`.
