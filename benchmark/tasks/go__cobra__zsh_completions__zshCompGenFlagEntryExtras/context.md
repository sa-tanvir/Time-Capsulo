# Context for the function to implement

- **Language:** go
- **File:** `zsh_completions.go`

## Imports / includes available in this file

```
import "encoding/json"
import "fmt"
import "io"
import "os"
import "sort"
import "strings"
import "text/template"
import "github.com/spf13/pflag"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(c*Command)GenZshCompletion w io . Writer
(c*Command)GenZshCompletionFile filename string
(c*Command)MarkZshCompPositionalArgumentFile argPosition int , patterns ... string
(c*Command)MarkZshCompPositionalArgumentWords argPosition int , words ... string
(c*Command)zshCompGetArgsAnnotations
(c*Command)zshCompSetArgsAnnotations annotation zshCompArgsAnnotation
(c*Command)zshcompArgsAnnotationnIsDuplicatePosition annotation zshCompArgsAnnotation , position int
(f*pflag.Flag)
zshCompExtractArgumentCompletionHintsForRendering c * Command
zshCompExtractFlag c * Command
zshCompFlagCouldBeSpecifiedMoreThenOnce f * pflag . Flag
zshCompGenFlagEntryForArguments f * pflag . Flag
zshCompGenFlagEntryForMultiOptionFlag f * pflag . Flag
zshCompGenFlagEntryForSingleOptionFlag f * pflag . Flag
zshCompGenFuncName c * Command
zshCompQuoteFlagDescription s string
zshCompRenderZshCompArgHint i int , z zshCompArgHint
```

## Package-level constants used by this function

```go
// zsh_completions.go
const zshCompDirname = "cobra_annotations_zsh_dirname"

// bash_completions.go (same package)
const BashCompFilenameExt = "cobra_annotation_bash_completion_filename_extensions"
```

## Relevant fields of `pflag.Flag` (github.com/spf13/pflag v1.0.3)

```go
type Flag struct {
	Name        string              // name as it appears on command line
	Shorthand   string              // one-letter abbreviated flag
	Usage       string              // help message
	Value       Value               // value as set
	DefValue    string              // default value (as text); for usage message
	NoOptDefVal string              // default value (as text); if the flag is on the command line without any options
	Annotations map[string][]string // used by cobra.Command bash autocomple code
	// ... (other fields not relevant here)
}
```

`MarkFlagFilename(flags, name, extensions...)` stores `extensions` under the
annotation key `BashCompFilenameExt`; `MarkFlagDirname(flags, name)` stores
`[]string{"-(/)"}` under the key `zshCompDirname`.
