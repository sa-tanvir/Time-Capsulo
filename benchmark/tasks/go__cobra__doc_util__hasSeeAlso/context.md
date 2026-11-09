# Context for the function to implement

- **Language:** go
- **File:** `doc/util.go`

## Imports / includes available in this file

```
import "strings"
import "github.com/spf13/cobra"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(s byName)Len
(s byName)Less i , j int
(s byName)Swap i , j int
forceMultiLine s string
```

## Relevant public API of `cobra.Command` (package `github.com/spf13/cobra`, v0.0.5)

```go
// HasParent determines if the command is a child command.
func (c *Command) HasParent() bool
// Parent returns a commands parent command.
func (c *Command) Parent() *Command
// Commands returns a sorted slice of child commands (sorted by name in place when
// cobra.EnableCommandSorting is true, the default).
func (c *Command) Commands() []*Command
// Name returns the command's name: the first word in the Use line.
func (c *Command) Name() string
// CommandPath returns the full path to this command, e.g. "root sub subsub".
func (c *Command) CommandPath() string
// IsAvailableCommand determines if a command is available as a non-help command:
// false if deprecated or hidden, false if it is its parent's auto-generated help command,
// otherwise true if it is runnable or has available sub commands.
func (c *Command) IsAvailableCommand() bool
// IsAdditionalHelpTopicCommand determines if a command is an additional help topic command:
// it is NOT runnable/hidden/deprecated, and has no sub commands that are not help topics.
func (c *Command) IsAdditionalHelpTopicCommand() bool
```
