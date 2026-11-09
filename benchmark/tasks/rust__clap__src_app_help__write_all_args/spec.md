# Functional specification: `Help::write_all_args(&mut self, parser: &Parser) -> ClapResult<()>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). It writes the argument sections of
a help screen: the `FLAGS:`, `OPTIONS:`, `ARGS:` and `SUBCOMMANDS:` blocks that follow
the `USAGE:` line, e.g.

```
FLAGS:
    -h, --help       Prints help information
    -V, --version    Prints version information

OPTIONS:
    -o, --option <opt>    tests options

ARGS:
    <positional>    tests positionals

SUBCOMMANDS:
    help      Prints this message or the help of the given subcommand(s)
    subcmd    tests subcommands
```

It decides which sections exist, in what order, with which header, and how they are
separated; the entries themselves are produced by the sibling section writers listed in
the context. The help-output tests compare whole help screens.

## 2. Functional requirements

1. **Which sections exist.**
   - flags: `parser.has_flags()`; options: `parser.has_opts()` (both true even if every
     element is hidden);
   - positionals: at least one positional **without** `ArgSettings::Hidden`;
   - subcommands: `parser.has_visible_subcommands()`.
2. **Unified mode.** If the parser has `AppSettings::UnifiedHelpMessage` **and** there
   are flags or options, write a single section with header `OPTIONS:\n` whose entries
   are all flags followed by all options, passed together (flags first, then options,
   as one iterator) to `self.write_args` (which sorts them).
3. **Normal mode** (otherwise):
   - if there are flags: header `FLAGS:\n`, then `write_args` over the flags;
   - if there are options: header `OPTIONS:\n`, then `write_args` over the options.
4. **Positionals** (both modes): header `ARGS:\n`, then `write_args_unsorted` over all
   positionals (in index order; the writer itself skips hidden ones).
5. **Subcommands**: header `SUBCOMMANDS:\n`, then `write_subcommands(parser)`.
6. **Order and separation.** Sections appear in the order flags, options (or the unified
   options section), args, subcommands. Before every section except the first one
   written, write `"\n\n"`. Nothing is written before the first header or after the last
   entry (no trailing newline). If no section exists, nothing is written at all.
7. **Headers** are written in the "warning" colour style (`color!(self, "…", warning)`;
   plain text when colours are off). Separators are written plain.
8. Errors from writing are converted to the crate error type and returned immediately;
   on success return `Ok(())`.

Example: an app with only positionals `<a>` and `<b>` (help "first"/"second") writes

```
ARGS:
    <a>    first
    <b>    second
```

An app with UnifiedHelpMessage, flag `-f` and option `--opt <x>` writes a single
`OPTIONS:` section containing both entries; without the setting it writes `FLAGS:`
(with `-f`), a blank line, then `OPTIONS:` (with `--opt`). A subcommand named `help`
alone does not create a `SUBCOMMANDS:` section; if other visible subcommands exist, the
section lists all non-hidden subcommands including `help`.

## 3. Input specification

- `self`: the help writer (see "Instance state"); the section writers update
  `self.longest` and `self.force_next_line` themselves.
- `parser`: a fully built `Parser` (flags, options, positionals, subcommands, settings).

## 4. Output specification

- Writes the sections to `self.writer`; returns `ClapResult<()>`.

## 5. Edge cases and constraints

- If every positional is hidden, no `ARGS:` section is written (not even a header).
- If all flags (or options) are hidden, the header is still written, followed by no
  entries.
- In unified mode with no flags and no options, no `OPTIONS:` section is written, but
  `ARGS:`/`SUBCOMMANDS:` still follow the normal rules (the first written section has no
  leading `"\n\n"`).
- Does not change parser state.
