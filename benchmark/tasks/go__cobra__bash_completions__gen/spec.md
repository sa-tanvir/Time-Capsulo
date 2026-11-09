# Functional specification: `func gen(buf *bytes.Buffer, cmd *Command)`

## 1. Component overview

Package `cobra` (`github.com/spf13/cobra`) generates a bash completion script
for a command tree (`Command.GenBashCompletion`). The script contains one bash
function per (available) command, which records the command's sub-commands,
flags, required flags, valid nouns and noun aliases in bash arrays.
`GenBashCompletion` writes a fixed preamble, then calls `gen(buf, root)`, then
a fixed postscript. `gen` appends to `buf` the bash functions for `cmd` and,
recursively, for all of its available descendants.

## 2. Functional requirements

1. **Descendants first.** For each child `c` of `cmd`, in the order returned
   by `cmd.Commands()` (sorted by name), skip it if it is not available
   (`!c.IsAvailableCommand()`) or if it is `cmd`'s own help command
   (`cmd.helpCommand`); otherwise recursively emit the functions for `c` (and
   its descendants). All of this is written **before** `cmd`'s own function,
   so the output is in post-order (deepest functions first, `cmd` last).
   Hidden, deprecated and non-available commands are skipped together with
   their whole subtree.
2. **Function name.** Take `cmd.CommandPath()` (names separated by single
   spaces), replace every space with `_` and then every `:` with `__`. Call
   the result `N`. Example: path `root echo times` → `root_echo_times`;
   `root cmd:colon` → `root_cmd__colon`.
3. **Header.** If `cmd` is the root of its tree (`cmd.Root() == cmd`), write
   `_N_root_command()` followed by a newline and `{` and a newline; otherwise
   write `_N()`, newline, `{`, newline.
4. Then write, each followed by a newline:
   - `    last_command="N"` — four spaces, then `last_command=` and `N` as a Go
     double-quoted string literal (`fmt.Sprintf("%q", N)`);
   - an empty line;
   - `    command_aliases=()`;
   - an empty line.
5. Then append, in this order, the blocks produced by `writeCommands(buf, cmd)`,
   `writeFlags(buf, cmd)`, `writeRequiredFlag(buf, cmd)`,
   `writeRequiredNouns(buf, cmd)` and `writeArgAliases(buf, cmd)`.
6. Finally write `}` followed by two newlines (`"}\n\n"`).
7. Nothing is written before the first function or between functions other
   than what is described above. The function returns nothing; it writes only
   to `buf` (the helpers sort `ValidArgs`, `ArgAliases` and `Aliases` of the
   visited commands in place, and `Commands()` sorts child lists in place).

Example: for a root `root` (runnable) with runnable children `echo` (which
has a runnable child `times`) and `print`, plus a hidden child, the output
consists of the functions `_root_echo_times()`, `_root_echo()`, `_root_print()`
and finally `_root_root_command()`, in that order. The function for `echo`
starts with:

```
_root_echo()
{
    last_command="root_echo"

    command_aliases=()

    commands=()
    ...
```

and every function ends with the `noun_aliases` block followed by `}` and an
empty line.

## 3. Input specification

- `buf`: a non-nil `*bytes.Buffer`; output is appended to its current content.
- `cmd`: a non-nil `*Command`, either the root of a tree or any sub-command.
  The tree may be arbitrarily deep, with hidden/deprecated commands, aliases,
  valid args, arg aliases and flags with completion annotations.

## 4. Output specification

- No return value; the generated text is appended to `buf`.

## 5. Edge cases and constraints

- If `cmd` is not the root, its own header uses `_N()` (not `_root_command`),
  even though it is the top-most function emitted by this call.
- A command with no children produces exactly one function.
- Unavailable children produce no output at all, not even for their
  available descendants.
- Not safe for concurrent use on the same tree.
