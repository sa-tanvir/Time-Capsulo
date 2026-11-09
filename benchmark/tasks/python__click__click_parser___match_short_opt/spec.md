# Functional specification: `OptionParser._match_short_opt(self, arg, state)`

## 1. Component overview

`click.parser.OptionParser` is click's low-level command-line parser. When a
token such as `-v`, `-vvv`, `-xvf`, `-ofile.txt` or `+a` could not be matched
as a long option, it is handled as a **cluster of short (one-character)
options** sharing one prefix character. `_match_short_opt` processes such a
token: it walks its characters left to right, resolves each one to a
registered short option, collects values for options that take them, and
records everything in the parsing state. The relevant parser, option and state
attributes, plus `normalize_opt` and `_error_opt_args`, are shown in
`context.md`.

## 2. Functional requirements

1. `arg` is a string of at least two characters; `arg[0]` is the **prefix**
   (e.g. `-`, `+`, `/`) and every following character is one short option
   letter.
2. For each option character `ch`, in order, form the option string
   `prefix + ch` and normalise it with the parser's context
   (`normalize_opt(prefix + ch, self.ctx)`; e.g. a context whose
   `token_normalize_func` lower-cases tokens turns `-X` into `-x`). Look the
   normalised string up among the registered short option strings.
3. **Unknown character:**
   - If `self.ignore_unknown_options` is false, raise
     `click.exceptions.NoSuchOption` for the normalised option string with
     `ctx=self.ctx` (message `no such option: -f`; no possibilities).
     Options earlier in the same cluster have already been recorded.
   - If it is true, remember the (un-normalised) character and continue with
     the next one. After the whole token has been processed, if any characters
     were remembered, append **one** string `prefix + <remembered characters
     in order>` to `state.largs` (e.g. `-vvvvx` with only `-v` known yields
     four `-v` occurrences and `'-x'` in `largs`; `-foo` with nothing known
     yields `'-foo'`).
4. **Option without value** (`takes_value` false: flag, count, constant):
   record it with value `None` and continue with the next character.
5. **Option taking a value** (action `store`/`append`):
   - If characters remain in `arg` after this one, they form the option's
     first value (`-ofile.txt` → value `file.txt`; `-xvf foo`: if `-f`
     takes a value it gets the next argument). Processing of the token stops
     after this option — the remaining characters are **not** treated as
     options.
   - The option consumes `option.nargs` values in total, taken in order from
     the front: the attached remainder (if any) first, then `state.rargs`.
     Consumed values are removed from `state.rargs`.
   - If fewer than `nargs` values are available, raise
     `click.exceptions.BadOptionUsage` exactly as `_error_opt_args(nargs, opt)`
     does (it may simply be called): `option_name` is the normalised option
     string, the message is `<opt> option requires an argument`
     (`nargs == 1`) or `<opt> option requires <nargs> arguments`, and **no
     context is attached** (`ctx` is `None`, unlike `NoSuchOption`). When this
     happens after an attached remainder, that remainder has already been put
     at the front of `state.rargs` (`'-p1'` with `rargs == []` leaves
     `rargs == ['1']`).
   - The value is the single string when `nargs == 1`, else a `tuple` of
     `nargs` strings. Values are taken verbatim even if they look like
     options.
6. Every successfully resolved option is recorded with exactly one
   `option.process(value, state)` call, in the order the characters appear
   (so `-vvv` on a counting option gives a count of 3, and `-ab` records
   `a` then `b`).
7. Returns `None`.

Examples (`-a`, `-b` flags; `-v` count; `-o` store nargs 1; `-p` store nargs 2;
`ignore_unknown_options` false unless stated):

| arg, rargs before | effect |
|---|---|
| `'-ab'`, `[]` | `a`, `b` recorded (order `a`, `b`) |
| `'-vvv'`, `['x']` | `v` counted 3 times, rargs `['x']` |
| `'-ofoo'`, `['x']` | `o = 'foo'`, rargs `['x']` |
| `'-ao'`, `['x', 'y']` | `a` recorded, `o = 'x'`, rargs `['y']` |
| `'-oab'`, `[]` | `o = 'ab'` (`a`/`b` not treated as options) |
| `'-p1'`, `['2', '3']` | `p = ('1', '2')`, rargs `['3']` |
| `'-o'`, `[]` | `BadOptionUsage`: `-o option requires an argument` |
| `'-p'`, `['1']` | `BadOptionUsage`: `-p option requires 2 arguments` |
| `'-f'`, `[]` | `NoSuchOption`: `no such option: -f` |
| `'-axb'` (ignore unknown) | `a`, `b` recorded, `largs` gets `'-x'` |

## 3. Input specification

| Parameter | Type | Meaning |
|---|---|---|
| `self` | `OptionParser` | Registered options; `self.ctx` (`Context` or `None`, may define `token_normalize_func`); `self.ignore_unknown_options` (bool). |
| `arg` | `str` | The whole token, prefix included, length ≥ 2. |
| `state` | `ParsingState` | `rargs`: list of remaining `str` arguments; `largs`: list of leftover arguments. |

## 4. Output specification

Returns `None`. Effects: `option.process` calls update `state.opts` and
`state.order`; consumed values are removed from `state.rargs`; with
`ignore_unknown_options`, at most one string is appended to `state.largs`.
Errors: `NoSuchOption` / `BadOptionUsage` (subclasses of `click.UsageError`)
carrying the normalised option string as `option_name`; `NoSuchOption` gets
`ctx=self.ctx`, `BadOptionUsage` gets no context (`ctx` is `None`).

## 5. Edge cases and constraints

- The prefix is reused for every character: `+ab` means `+a`, `+b`.
- A character equal to the prefix or a non-letter is looked up like any
  other (e.g. `--` inside `-a-` is the option `--`, normally unknown).
- When unknown characters are ignored and an option taking a value appears,
  the remainder after it is that option's value; only characters before it
  can end up in `largs`.
- Lookup uses the normalised string, while the `largs` entry is built from
  the original characters.
- Mutates `state` in place; does not change the parser's registrations.
