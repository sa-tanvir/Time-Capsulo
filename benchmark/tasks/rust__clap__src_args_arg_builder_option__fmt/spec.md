# Functional specification: `impl Display for OptBuilder` — `fmt(&self, f: &mut Formatter) -> Result`

## 1. Component overview

Part of `clap` 2.30, a command-line argument parser. An `OptBuilder` is the internal
representation of an *option*: an argument that is introduced by a switch (`-o` or
`--option`) and takes one or more values. Its `Display` implementation renders the
option's "signature", e.g. `--config <FILE>`, which clap embeds in usage strings, help
screens (`USAGE:` lines, `OPTIONS:` entries, "required arguments were not provided"
lists) and error messages ("The argument '--opt <val>' requires a value…"). Many help
and error-output tests compare whole rendered screens, so the text must match exactly.

## 2. Functional requirements

The output is the concatenation of a **switch part** and a **value part**; nothing else
(no help text, no aliases, no leading/trailing whitespace).

1. **Separator.** `sep` is `"="` if the option has the `ArgSettings::RequireEquals`
   setting, otherwise a single space `" "`.
2. **Switch part.** If the option has a long name `l`, write `--` + `l` + `sep`.
   Otherwise write `-` + the short character + `sep`. (The short form is used only when
   there is no long name; when both exist, only the long form appears.)
3. **Value delimiter.** `delim` is the option's value delimiter character if the option
   has `ArgSettings::RequireDelimiter`; otherwise a single space.
4. **Value part**, first matching rule:
   - **Value names present** (`self.v.val_names` is `Some`): write each value name as
     `<name>`, in ascending key order of the map, with `delim` between consecutive names
     (not before the first or after the last). If the option has `ArgSettings::Multiple`
     **and exactly one** value name exists, append `...`.
   - **Else, a fixed number of values** (`self.v.num_vals` is `Some(n)`): write `<NAME>`
     `n` times, where `NAME` is the option's own name (`self.b.name`), separated by
     `delim`. If `Multiple` is set and `n == 1`, append `...`. `n == 0` writes nothing.
   - **Else:** write `<NAME>` (the option's name), followed by `...` if `Multiple` is set.
5. Aliases, help text, possible values, defaults and all other settings do not affect
   the output.
6. Write everything through the given `Formatter` (`write!(f, …)`), propagating any
   `fmt::Error`; return `Ok(())` on success.

Examples (`name` is the option's internal name):

| long | short | name | value names | num_vals | settings | output |
|---|---|---|---|---|---|---|
| `option` | – | `opt` | – | – | Multiple | `--option <opt>...` |
| – | `o` | `opt` | `file`, `name` | – | – | `-o <file> <name>` |
| – | `o` | `opt` | `file`, `name` | – | Multiple | `-o <file> <name>` |
| `option` | – | `opt` | – | – | (has visible aliases) | `--option <opt>` |
| `opt` | `o` | `o` | `FILE` | – | RequireEquals | `--opt=<FILE>` |
| `opt` | `o` | `o` | `FILE` | – | RequireEquals, Multiple | `--opt=<FILE>...` |
| `fake` | `f` | `fake` | `some`, `val` | 2 | RequireDelimiter, delimiter `:` | `--fake <some>:<val>` |
| `opt` | – | `o` | – | 3 | Multiple, RequireDelimiter, delimiter `,` | `--opt <o>,<o>,<o>` |
| `opt` | – | `o` | – | 1 | Multiple | `--opt <o>...` |

## 3. Input specification

- `self`: an `OptBuilder` (see the "Instance state" section of the context). `self.s.long`
  is `Option<&str>` without leading dashes; `self.s.short` is `Option<char>`; at least
  one of them is set for every option clap builds.
- `self.v.val_names`: `Option<VecMap<&str>>`, keys are positions `0, 1, 2, …`.
- `self.v.num_vals`: `Option<u64>`; when both value names and `num_vals` are set, the
  value names win.
- `self.v.val_delim`: `Option<char>`; always `Some` when `RequireDelimiter` is set.
- Names may contain any Unicode text; it is copied verbatim.

## 4. Output specification

- Writes the signature into `f` and returns `std::fmt::Result` (`Ok(())`, or the error
  of a failed write).
- The result is a pure function of the fields listed above; repeated formatting yields
  identical text.

## 5. Edge cases and constraints

- No long and no short name: not a valid option; panicking is acceptable.
- `RequireDelimiter` without a delimiter: internal error; panicking (with
  `INTERNAL_ERROR_MSG`) is acceptable.
- The `...` suffix appears only for a single value slot (one value name, `num_vals == 1`,
  or the plain `<NAME>` form); never after two or more values.
- An empty value-name map produces an empty value part (the output is just the switch
  part including `sep`).
- Must not mutate `self`; must be cheap enough to be called for every help line
  (linear in the number of value names / values).
