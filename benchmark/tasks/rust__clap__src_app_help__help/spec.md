# Functional specification: `Help::help(&mut self, arg: &ArgWithDisplay, spec_vals: &str) -> io::Result<()>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). Each argument entry of a help
screen is written as: short switch, long switch, value placeholders + padding (which
also decides `self.force_next_line`), and finally **the help text**, written by this
method. It chooses short or long help, appends the special-values suffix, wraps the
text to the terminal width when needed, and indents continuation lines so they line up
under the help column. Example (terminal width 120, `longest` = 14):

```
    -o, --option <opt>    first line
                          second line
```

or, in "next line" mode:

```
    -o, --option <opt>
            first line
            second line
```

The help-output tests compare whole screens (including the `{n}` line-break marker,
wrapping at the terminal width and long-help mode), so the exact layout matters.

## 2. Functional requirements

1. **Text selection.** If `self.use_long`: `h = arg.long_help()`, falling back to
   `arg.help()`, then `""`. Otherwise: `h = arg.help()`, falling back to
   `arg.long_help()`, then `""`. The text to print is `help = h + spec_vals`.
2. **Mode.** `nlh = self.next_line_help || arg has ArgSettings::NextLineHelp ||
   self.use_long`. The entry is in *next-line mode* when `nlh || self.force_next_line`.
3. **Indent width.** `spcs = 12` in next-line mode, else `self.longest + 12`.
4. **Too long?** `too_long = spcs + str_width(h) + str_width(spec_vals) >= self.term_w`.
5. **Line start.** In next-line mode, first write `"\n"` followed by 12 spaces (three
   `TAB`s).
6. **Wrapping.** If `(too_long && spcs <= self.term_w)` **or** `h` contains the marker
   `{n}`: replace every `{n}` in `help` by `"\n"` and wrap the result with
   `wrap_help(text, self.term_w - spcs)` (wraps each existing line separately to that
   many columns, without breaking words). Otherwise `help` is used unchanged (a `{n}` in
   `spec_vals` alone does not trigger wrapping or replacement).
7. **Writing lines.** Split `help` into lines (`str::lines` semantics: split at `\n`,
   a trailing newline does not create an empty last line, an empty text has no lines).
   Write the first line as-is. For every further line write `"\n"`, then the indent,
   then the line, where the indent is:
   - 12 spaces in next-line mode;
   - otherwise `self.longest + 12` spaces if the argument has a switch
     (`arg.has_switch()`), or `self.longest + 8` spaces for a positional.
8. **Trailing newline.** If, after wrapping, `help` contains no `'\n'` and the entry is
   in next-line mode, write a final `"\n"`.
9. Return `Ok(())`; propagate write errors immediately.

Examples (`term_w` = 120, no colour, `longest` = 14, option argument):

| help | spec_vals | mode | written |
|---|---|---|---|
| `"some help"` | `""` | normal | `some help` |
| `"line one{n}line two"` | `""` | normal | `line one` `\n` + 26 spaces + `line two` |
| same, positional | `""` | normal | `line one` `\n` + 22 spaces + `line two` |
| `"Some vals"` | `" [possible values: fast, slow]"` | normal | `Some vals [possible values: fast, slow]` |
| `"prints help"` | `""` | next-line (`next_line_help`) | `\n` + 12 spaces + `prints help` + `\n` |
| `"has{n}break"` | `""` | next-line | `\n` + 12 sp + `has` + `\n` + 12 sp + `break` |
| none | `""` | normal | nothing |
| none | `""` | next-line | `\n` + 12 spaces + `\n` |

With `term_w = 60`, `longest = 20`, a 40-word help is wrapped to `60 - 32 = 28`
columns and every continuation line is indented by 32 spaces.

## 3. Input specification

- `self`: the help writer (see "Instance state"): reads `use_long`, `next_line_help`,
  `force_next_line`, `longest`, `term_w` (may be `usize::MAX` = unlimited); writes to
  `self.writer`. Does not modify any field.
- `arg`: a flag, option, positional or subcommand entry (via `AnyArg`).
- `spec_vals`: suffix produced by `spec_vals` (empty or starting with a space).
- Texts may contain any Unicode and real newlines; widths are display widths.

## 4. Output specification

- Writes the help text as described to `self.writer`; returns `io::Result<()>`.

## 5. Edge cases and constraints

- Real `"\n"` characters in the help are always honoured as line breaks (every line is
  re-indented), even when no wrapping happens.
- When `spcs > term_w` the text is not wrapped because of its length (only a `{n}`
  marker triggers wrapping then); callers never combine `{n}` with `spcs > term_w`.
- With `term_w == usize::MAX` text is never too long; only `{n}` triggers wrapping.
- In long-help mode (`use_long`) the entry is always in next-line mode.
- Cost should be linear in the help length (plus the wrapping).
