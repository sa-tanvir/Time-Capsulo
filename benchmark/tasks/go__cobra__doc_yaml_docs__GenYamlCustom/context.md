# Context for the function to implement

- **Language:** go
- **File:** `doc/yaml_docs.go`

## Imports / includes available in this file

```
import "fmt"
import "io"
import "os"
import "path/filepath"
import "sort"
import "strings"
import "github.com/spf13/cobra"
import "github.com/spf13/pflag"
import "gopkg.in/yaml.v2"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(flag*pflag.Flag)
(s string)string
GenYamlTreeCustom cmd * cobra . Command , dir string , filePrepender , linkHandler func string string
genFlagResult flags * pflag . FlagSet
```

## Other package-level helpers of package `doc` (file `doc/util.go`, same package)

```go
// hasSeeAlso reports whether cmd needs a "SEE ALSO" section: true if cmd has a parent,
// or if it has at least one child that is available (IsAvailableCommand) and not an
// additional help topic (IsAdditionalHelpTopicCommand).
func hasSeeAlso(cmd *cobra.Command) bool

// forceMultiLine appends "\n" to s if len(s) > 60 and s contains no "\n"; otherwise returns s.
func forceMultiLine(s string) string

// byName implements sort.Interface, ordering commands by Name().
type byName []*cobra.Command
```

## Types defined in the same file

```go
type cmdOption struct {
	Name         string
	Shorthand    string `yaml:",omitempty"`
	DefaultValue string `yaml:"default_value,omitempty"`
	Usage        string `yaml:",omitempty"`
}

type cmdDoc struct {
	Name             string
	Synopsis         string      `yaml:",omitempty"`
	Description      string      `yaml:",omitempty"`
	Options          []cmdOption `yaml:",omitempty"`
	InheritedOptions []cmdOption `yaml:"inherited_options,omitempty"`
	Example          string      `yaml:",omitempty"`
	SeeAlso          []string    `yaml:"see_also,omitempty"`
}
```

`genFlagResult(flags)` returns one `cmdOption` per flag of the set (all flags, including
hidden/deprecated ones, in the set's lexicographic order), with `Name`, `Shorthand`,
`DefaultValue` and `Usage` filled from the flag (long usage/default texts passed through
`forceMultiLine`). It returns nil for an empty set.

## Relevant public API of `cobra.Command` (v0.0.5)

```go
func (c *Command) InitDefaultHelpCmd()   // adds the auto-generated "help" child if c has sub-commands (idempotent)
func (c *Command) InitDefaultHelpFlag()  // adds the "--help/-h" bool flag to c.Flags() if missing (idempotent)
func (c *Command) CommandPath() string   // e.g. "root echo times"
func (c *Command) Name() string
func (c *Command) HasParent() bool
func (c *Command) Parent() *Command
func (c *Command) Commands() []*Command  // child commands (the command's own slice)
func (c *Command) IsAvailableCommand() bool
func (c *Command) IsAdditionalHelpTopicCommand() bool
func (c *Command) NonInheritedFlags() *pflag.FlagSet // the command's own (local + its persistent) flags
func (c *Command) InheritedFlags() *pflag.FlagSet    // persistent flags inherited from ancestors
// fields: Short, Long, Example string
// (*pflag.FlagSet).HasFlags() bool reports whether the set contains any flag (hidden ones included).
```
