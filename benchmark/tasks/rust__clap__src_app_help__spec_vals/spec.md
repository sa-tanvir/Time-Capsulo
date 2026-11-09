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
