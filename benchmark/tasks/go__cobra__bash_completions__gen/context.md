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
