# Context for the function to implement

- **Language:** go
- **File:** `doc/man_docs.go`

## Imports / includes available in this file

```
import "bytes"
import "fmt"
import "io"
import "os"
import "path/filepath"
import "sort"
import "strconv"
import "strings"
import "time"
import "github.com/cpuguy83/go-md2man/md2man"
import "github.com/spf13/cobra"
import "github.com/spf13/pflag"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(c*cobra.Command)
(flag*pflag.Flag)
GenMan cmd * cobra . Command , header * GenManHeader , w io . Writer
GenManTree cmd * cobra . Command , header * GenManHeader , dir string
GenManTreeFromOpts cmd * cobra . Command , opts GenManTreeOptions
fillHeader header * GenManHeader , name string
manPreamble buf * bytes . Buffer , header * GenManHeader , cmd * cobra . Command , dashedName string
manPrintFlags buf * bytes . Buffer , flags * pflag . FlagSet
manPrintOptions buf * bytes . Buffer , command * cobra . Command
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

## Header type (same file)

```go
// GenManHeader is a lot like the .TH header at the start of man pages. These
// include the title, section, date, source, and manual.
type GenManHeader struct {
	Title   string
	Section string
	Date    *time.Time
	date    string // Date pre-formatted as "Jan 2006"; filled in by fillHeader
	Source  string
	Manual  string
}
```

`genMan` is called by `GenMan(cmd, header, w)` only **after** `fillHeader(header, cmd.CommandPath())`
has completed the header: `Title`, `Section`, `Date` (non-nil), `date` and `Source` are all set.
`GenMan` then converts the Markdown returned by `genMan` to roff with `md2man.Render`.

## What the same-file helpers write

- `manPreamble(buf, header, cmd, dashedName)` writes the title block
  (`% TITLE(SECTION)date`, `% source`, `% manual`), then `# NAME` with
  `<dashedName> \- <cmd.Short>`, `# SYNOPSIS` with `**<cmd.UseLine()>**`, and
  `# DESCRIPTION` with `cmd.Long` (or `cmd.Short` if `Long` is empty), followed by a blank line.
- `manPrintOptions(buf, cmd)` writes `# OPTIONS` (the command's non-inherited flags) and
  `# OPTIONS INHERITED FROM PARENT COMMANDS` (inherited flags), each only when the set has
  visible flags; hidden and deprecated flags are skipped.

## Relevant public API of `cobra.Command` (v0.0.5)

```go
func (c *Command) InitDefaultHelpCmd()   // adds the auto-generated "help" child if c has sub-commands (idempotent)
func (c *Command) InitDefaultHelpFlag()  // adds the "--help/-h" bool flag to c.Flags() if missing (idempotent)
func (c *Command) CommandPath() string   // e.g. "root echo times"
func (c *Command) Name() string
func (c *Command) HasParent() bool
func (c *Command) Parent() *Command
func (c *Command) VisitParents(fn func(*Command)) // calls fn on the parent, grand-parent, ... up to the root
func (c *Command) Commands() []*Command           // child commands (the command's own slice)
func (c *Command) IsAvailableCommand() bool
func (c *Command) IsAdditionalHelpTopicCommand() bool
// fields: Example string, DisableAutoGenTag bool
```
