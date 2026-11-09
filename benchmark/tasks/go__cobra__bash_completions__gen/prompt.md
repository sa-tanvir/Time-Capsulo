You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `bash_completions.go`

## Imports / includes available in this file

```
import "bytes"
import "fmt"
import "io"
import "os"
import "sort"
import "strings"
import "github.com/spf13/pflag"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(c*Command)GenBashCompletion w io . Writer
(c*Command)GenBashCompletionFile filename string
(flag*pflag.Flag)
nonCompletableFlag flag * pflag . Flag
writeArgAliases buf * bytes . Buffer , cmd * Command
writeCmdAliases buf * bytes . Buffer , cmd * Command
writeCommands buf * bytes . Buffer , cmd * Command
writeFlag buf * bytes . Buffer , flag * pflag . Flag , cmd * Command
writeFlagHandler buf * bytes . Buffer , name string , annotations map [ string ] [ ] string , cmd * Command
writeFlags buf * bytes . Buffer , cmd * Command
writeLocalNonPersistentFlag buf * bytes . Buffer , flag * pflag . Flag
writePostscript buf * bytes . Buffer , name string
writeRequiredFlag buf * bytes . Buffer , cmd * Command
writeRequiredNouns buf * bytes . Buffer , cmd * Command
writeShortFlag buf * bytes . Buffer , flag * pflag . Flag , cmd * Command
```

## What the per-section helpers write (same file)

Each helper appends one block of the bash function body to `buf`:

- `writeCommands(buf, cmd)`: `    commands=()` followed by one `    commands+=("<name>")` line per
  available, non-help child (plus that child's alias lines), then an empty line.
- `writeFlags(buf, cmd)`: the `flags=()`, `two_word_flags=()`, `local_nonpersistent_flags=()`,
  `flags_with_completion=()`, `flags_completion=()` declarations and one entry per completable
  flag of `cmd` (own and inherited), then an empty line.
- `writeRequiredFlag(buf, cmd)`: `    must_have_one_flag=()` plus one line per required flag.
- `writeRequiredNouns(buf, cmd)`: `    must_have_one_noun=()` plus one line per entry of
  `cmd.ValidArgs` (sorted).
- `writeArgAliases(buf, cmd)`: `    noun_aliases=()` plus one line per entry of `cmd.ArgAliases`
  (sorted).

## Instance state / `Command` API used (same package)

```go
type Command struct {
	// ...
	// helpCommand is the command used for help (the auto-generated "help" child that
	// InitDefaultHelpCmd adds); nil if none was installed on this command.
	helpCommand *Command
	// ...
}

// Commands returns the child commands, sorted by name (in place) when EnableCommandSorting is true.
func (c *Command) Commands() []*Command
// IsAvailableCommand: false if deprecated, hidden, or the parent's help command; otherwise true
// if runnable or it has available sub commands.
func (c *Command) IsAvailableCommand() bool
// CommandPath returns the full path, e.g. "root echo times".
func (c *Command) CommandPath() string
// Root finds the root command.
func (c *Command) Root() *Command
```

=== STUB ===
```go
func gen(buf *bytes.Buffer, cmd *Command) {
    // TODO: implement according to the specification
}
```
