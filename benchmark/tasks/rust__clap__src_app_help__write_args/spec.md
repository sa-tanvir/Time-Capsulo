# Functional specification: `Help::write_args(&mut self, args: I) -> io::Result<()>`

where `I: Iterator<Item = &'d ArgWithOrder<'b, 'c>>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). It writes the body of one help
section (the lines under `FLAGS:`, `OPTIONS:`, …) for a sequence of arguments:

```
    -d               Turn debugging information on
    -h, --help       Prints help information
    -V, --version    Prints version information
```

It decides which arguments are shown, computes the alignment width shared by the
section, orders the entries and writes them one per line using the sibling `write_arg`.
Most help-output tests depend on its ordering and alignment.

## 2. Functional requirements

1. **Visibility filter.** An argument is shown if it is **not** `Hidden`, or if it has
   `NextLineHelp` (a hidden argument with `NextLineHelp` is still shown). All other
   arguments are ignored completely.
2. **Column width.** Set `self.longest` to `max(2, w₁, w₂, …)` where `wᵢ` is the display
   width (`str_width`) of the signature (`to_string()`) of every *shown* argument whose
   `longest_filter()` is true. (2 is the width of the shortest legal switch `-x`.)
   `self.longest` is reset at the start, so earlier values do not matter, and it keeps
   the computed value after the call.
3. **Order.** Entries are ordered by `disp_ord()` ascending, and among equal display
   orders by `name()` in ascending (byte-wise string) order. If two shown arguments had
   the same display order and the same name, only the last one given would be written
   (names are unique in practice).
4. **Writing.** Write each shown argument with `self.write_arg(arg.as_base())`, in the
   order above, writing a single `"\n"` **between** consecutive entries (none before the
   first or after the last). With no shown arguments nothing is written.
5. Return `Ok(())`; propagate the first I/O error.

Example: flags `-d` (help "Turn debugging information on"), `--help`/`-h`,
`--version`/`-V`, all with default display order 999. Widths counted: `--help` (6) and
`--version` (9); `-d` has no long switch so it does not count; `longest = 9`. Sorted by
name: `debug`, `help`, `version`, producing the three lines shown in §1 joined by `"\n"`.

With display orders `b`→0, `a`→999, `c`→0, the order is `b`, `c`, `a`.

## 3. Input specification

- `self`: the help writer (see "Instance state"); `write_arg` reads `longest`,
  `term_w`, `next_line_help`, etc.
- `args`: any iterator over flags, options and/or positionals (e.g. flags chained with
  options for a unified section). It is consumed once.

## 4. Output specification

- Entries written to `self.writer`; `self.longest` updated as described;
  returns `io::Result<()>`.

## 5. Edge cases and constraints

- Hidden arguments without `NextLineHelp` neither appear nor influence `longest`.
- Flags with only a short switch appear but never widen the column.
- An empty iterator (or all hidden) writes nothing and leaves `longest = 2`.
- Must scale to thousands of arguments (sorting cost `O(n log n)`).
