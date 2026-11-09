# Functional specification: `MultiCommand.format_commands(self, ctx, formatter)`

## 1. Component overview

`MultiCommand.format_commands` writes the `Commands:` section of a group's
`--help` page: one row per visible subcommand, with the subcommand name on the
left and its short help on the right. It is called by the help machinery after
the options section has been written. The members it relies on
(`list_commands`, `get_command`, `Command.hidden`,
`Command.get_short_help_str`, `HelpFormatter.width`, `HelpFormatter.section`,
`HelpFormatter.write_dl`) are described in `context.md`.

## 2. Functional requirements

1. **Collect the visible subcommands.** Ask `self.list_commands(ctx)` for the
   subcommand names and, for each name in the order returned, look the command
   up with `self.get_command(ctx, name)`.
   - If the lookup returns `None` (a name was listed that does not exist),
     silently ignore that name.
   - If the command is hidden (`cmd.hidden` truthy), ignore it. A hidden
     subgroup is ignored as a whole; its own subcommands are never listed here.
   - Otherwise keep the pair (listed name, command). Duplicate names are kept
     as many times as they are listed.
2. **Nothing to show.** If no subcommand was kept, write nothing at all to the
   formatter (no heading, no blank line).
3. **Short-help width.** Compute `limit = formatter.width - 6 - L`, where `L`
   is the length (in characters) of the longest *listed name* among the kept
   subcommands. (The listed name is used, not `cmd.name`.)
4. **Rows.** For each kept subcommand, in order, build the row
   `(listed_name, cmd.get_short_help_str(limit))`. The short help is therefore
   the command's explicit `short_help` if it has one, otherwise its help text
   condensed to `limit` characters, or `''`.
5. **Output.** Inside `formatter.section('Commands')`, write all rows with a
   single `formatter.write_dl(rows)` call (default column arguments).
6. Return `None`.

Example: a group with subcommands registered as `short` (help
`"This is a short text."`), `special-chars` (help
`"Login and store the token in ~/.netrc."`) and `long` (help
`"This is a long text that is too long to show as short help\n and will be truncated instead."`),
formatted with an 80-column formatter, yields (names sorted by the group):

```
Commands:
  long           This is a long text that is too long to show as short help...
  short          This is a short text.
  special-chars  Login and store the token in ~/.netrc.
```

Here `L = 13` (`special-chars`), so `limit = 80 - 6 - 13 = 61`.

A group whose only subcommand is `hidden=True` (or a hidden subgroup) produces
no `Commands:` section, and neither the hidden name nor the names of the
hidden subgroup's children appear in the help output.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `self` | `click.MultiCommand` (e.g. `click.Group`) | The command whose subcommands are listed. |
| `ctx` | `click.Context` | Current context; only passed through to `list_commands` / `get_command`. |
| `formatter` | `click.HelpFormatter` | Output sink; its `width` (int, columns) is read. |

## 4. Output specification

Returns `None`. The effect is the text written into `formatter`: either nothing,
or exactly one `Commands` section containing one definition-list row per visible
subcommand, in `list_commands` order. `self`, `ctx` and the subcommands are not
modified.

## 5. Edge cases and constraints

- Empty `list_commands` result, all names unknown, or all commands hidden: no
  output.
- `limit` may become small or negative for very long names or narrow
  formatters; it is passed to `get_short_help_str` unchanged.
- Commands with an explicit `short_help` show it verbatim regardless of
  `limit`; commands without any help get an empty description.
- Works for chained groups and groups with arguments exactly the same way.
- No I/O other than writing to the given formatter.
