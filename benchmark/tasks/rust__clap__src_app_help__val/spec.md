# Functional specification: `Help::val(&mut self, arg: &ArgWithDisplay) -> Result<String, io::Error>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). Each argument entry of a help
screen is written in four steps: the short switch, the long switch, then **`val`**, then
the help text. For example in

```
    -o, --option <file> <name>    some help [possible values: a, b]
    <input>...                    the input files
```

`val` writes the **value placeholders** (` <file> <name>`… after the switches; the whole
`<input>...` for a positional), then decides whether the help text must move to the next
line, writes the **padding spaces** that align the help column, and returns the
argument's "special values" suffix (`[default: …]`, `[possible values: …]`, …) for the
next step. The help-output tests compare entire screens, so every character and every
padding space counts.

## 2. Functional requirements

### 2.1 Value placeholders (only if `arg.takes_value()`)

Flags (`takes_value() == false`) write no placeholders. Otherwise, let `delim` be
`arg.val_delim()` if the argument has `ArgSettings::RequireDelimiter`, else a space.
All placeholders below are written in the "good" colour style (via `color!(…, good)`;
plain text when colours are off); delimiters are written plain.

1. If `arg.val_names()` is `Some(names)`: write `<name>` for every name in index order,
   with `delim` between consecutive ones. If the argument has `ArgSettings::Multiple`
   and there is exactly one name, then write `...`.
2. Else if `arg.num_vals()` is `Some(n)`: write `<NAME>` `n` times (`NAME` =
   `arg.name()`), separated by `delim`; if `Multiple` and `n == 1`, write `...`.
3. Else if the argument has a switch (an option): write `<NAME>`, plus `...` if
   `Multiple`.
4. Else (a positional without names or count): write the argument's own `Display`
   text (e.g. `<input>...`), styled "good".

Nothing is written before the placeholders (the separator after the long switch was
already written by the previous step).

### 2.2 Special values and line decision

- `spec = self.spec_vals(arg)` (sibling method; returns e.g. `" [default: x]"` or `""`).
- `h` = `arg.help()` or `""` (always the short help, even in long-help mode);
  `h_w = str_width(h) + str_width(spec)`.
- `nlh = self.next_line_help || arg has ArgSettings::NextLineHelp`.
- `taken = self.longest + 12`.
- Set **`self.force_next_line`** to true exactly when all hold: `!nlh`,
  `self.term_w >= taken`, `taken / term_w > 0.40` (computed as `f32` division), and
  `h_w > term_w - taken`; otherwise set it to false.

### 2.3 Padding (only when `!(nlh || self.force_next_line)`; otherwise write nothing more)

Let `w = str_width(arg.to_string())` (display width of the argument's signature).
- Argument with a switch: write `self.longest - w` spaces plus **4** more if the
  argument has a long name (`arg.long().is_some()`), or plus **8** more if it has only
  a short name.
- Positional: write `self.longest + 4 - w` spaces.

### 2.4 Result

Return `Ok(spec)`. Any I/O error from writing is returned as `Err` immediately.

### Examples (colour off, writer at the position after the switches)

| argument | `longest` | written by `val` | returns |
|---|---|---|---|
| option `--option`/`-o`, name `opt`, no value names, help `"h"` | 14 | `<opt>` + 4 spaces | `""` |
| option `-o` only, value names `file`,`name` | 16 | `<file> <name>` + 8 spaces | `""` |
| option `--fake`/`-f`, names `some`,`val`, RequireDelimiter `:` | 19 | `<some>:<val>` + 4 spaces | `""` |
| option `--opt`, `num_vals = 3`, Multiple, RequireDelimiter `,`, name `o` | 17 | `<o>,<o>,<o>` + 4 spaces | `""` |
| flag `--flag`/`-f`, longest 10 | 10 | 8 spaces (= 10 − 6 + 4) | `""` |
| positional `<input>...`, longest 12, possible values `vi`, `emacs` | 12 | `<input>...` + 6 spaces | `" [possible values: vi, emacs]"` |
| any argument with NextLineHelp | – | placeholders only, no padding | spec |

(`longest` is set by the section writer to the widest signature of the section; for
switches the signature is the `Display` text, e.g. `--option <opt>` has width 14.)

## 3. Input specification

- `self`: the help writer (see the "Instance state" section): reads `next_line_help`,
  `term_w` (may be `usize::MAX` = unlimited), `longest`, `color`/`cizer`, `hide_pv`;
  writes `force_next_line`; writes to `self.writer`.
- `arg`: flag, option or positional; `self.longest >= str_width(arg.to_string())` is
  guaranteed by the callers.
- Names and help text may contain any Unicode; widths are display widths
  (`str_width`), not byte lengths.

## 4. Output specification

- Bytes written to `self.writer` as described; `self.force_next_line` updated (always
  assigned, also for flags and positionals).
- Returns `Ok(String)` containing exactly what `self.spec_vals(arg)` returns.

## 5. Edge cases and constraints

- `...` is written only for a single value slot; two or more names/values never get it.
- `num_vals == Some(0)` writes no placeholders.
- `term_w < taken` never forces the next line; with `term_w == usize::MAX` the ratio
  is effectively 0, so the next line is never forced.
- When `nlh` or `force_next_line` is true, no padding is written (the help step will
  start a new line).
- The placeholders do not depend on `self.use_long`.
- Cost is linear in the number of value slots and the help/spec length.
