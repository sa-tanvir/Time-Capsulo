You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func hasSeeAlso(cmd *cobra.Command) bool`

## 1. Component overview

Package `doc` (`github.com/spf13/cobra/doc`) generates documentation (man
pages, Markdown, reStructuredText, YAML) for cobra command trees. Each
generated page may end with a "SEE ALSO" section that links to the parent
command and to the visible sub-commands. `hasSeeAlso` decides whether such a
section is needed for command `cmd`: it reports whether there is at least one
command worth linking to.

## 2. Functional requirements

Return `true` if and only if at least one of the following holds:

1. `cmd` has a parent command (`cmd.HasParent()`); a sub-command always links
   back to its parent.
2. `cmd` has at least one child command `c` (among `cmd.Commands()`) such that
   `c.IsAvailableCommand()` is true **and** `c.IsAdditionalHelpTopicCommand()`
   is false.

Otherwise return `false`. In particular a root command (no parent) with no
children, or whose children are all hidden, deprecated, its auto-generated
`help` command, not runnable without available sub-commands, or additional
help topics, has no "SEE ALSO" section.

The function only inspects the command tree. It has no other side effects
(apart from `Commands()` sorting the child list in place, which is the normal
behaviour of that accessor).

Examples:

| command | result |
|---|---|
| root with no children | false |
| any sub-command (has a parent), even without children | true |
| root with one runnable, visible child | true |
| root whose only children are hidden or deprecated | false |
| root whose only child is the auto-generated `help` command | false |
| root whose only child is not runnable and has no children (a help topic) | false |
| root with a non-runnable child that has a runnable visible grandchild | true |
| root with children `aaa` (hidden), `bbb` (runnable) | true |

## 3. Input specification

- `cmd`: a non-nil `*cobra.Command`, part of an arbitrary command tree (any
  depth and fan-out).

## 4. Output specification

- A `bool` as defined above.

## 5. Edge cases and constraints

- A child counts only if it is available **and** not an additional help topic.
- Having a parent is sufficient on its own, regardless of children.
- Deterministic; does not modify any command's fields.

=== CONTEXT ===
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

=== STUB ===
```go
func hasSeeAlso(cmd *cobra.Command) bool {
    // TODO: implement according to the specification
}
```
