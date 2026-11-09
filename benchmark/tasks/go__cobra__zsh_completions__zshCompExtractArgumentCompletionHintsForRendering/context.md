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
zshCompExtractFlag c * Command
zshCompFlagCouldBeSpecifiedMoreThenOnce f * pflag . Flag
zshCompGenFlagEntryExtras f * pflag . Flag
zshCompGenFlagEntryForArguments f * pflag . Flag
zshCompGenFlagEntryForMultiOptionFlag f * pflag . Flag
zshCompGenFlagEntryForSingleOptionFlag f * pflag . Flag
zshCompGenFuncName c * Command
zshCompQuoteFlagDescription s string
zshCompRenderZshCompArgHint i int , z zshCompArgHint
```

## Package-level constants and types used by this function and its helpers

```go
const (
	zshCompArgumentAnnotation   = "cobra_annotations_zsh_completion_argument_annotation"
	zshCompArgumentFilenameComp = "cobra_annotations_zsh_completion_argument_file_completion"
	zshCompArgumentWordComp     = "cobra_annotations_zsh_completion_argument_word_completion"
	zshCompDirname              = "cobra_annotations_zsh_dirname"
)

// zshCompArgsAnnotation is used to encode/decode zsh completion for
// arguments to/from Command.Annotations (key zshCompArgumentAnnotation, value = JSON).
// Map key = 1-based positional argument index.
type zshCompArgsAnnotation map[int]zshCompArgHint

type zshCompArgHint struct {
	// Indicates the type of the completion to use. One of:
	// zshCompArgumentFilenameComp or zshCompArgumentWordComp
	Tipe string `json:"type"`

	// A value for the type above (globs for file completion or words)
	Options []string `json:"options"`
}
```

## Relevant `Command` state and helper methods (same package)

```go
type Command struct {
	// ...
	// ValidArgs is list of all valid non-flag arguments that are accepted in bash completions
	ValidArgs []string
	// Annotations are key/value pairs that can be used by applications to identify or
	// group commands.
	Annotations map[string]string
	// ...
}

// zshCompGetArgsAnnotations decodes c.Annotations[zshCompArgumentAnnotation] (JSON) into a
// zshCompArgsAnnotation. A missing key yields an empty (non-nil) map and nil error; invalid
// JSON yields an error "Error unmarshaling zsh argument annotation: ...".
func (c *Command) zshCompGetArgsAnnotations() (zshCompArgsAnnotation, error)

// zshCompRenderZshCompArgHint renders one hint for positional argument i, e.g.
//   file hint,  i=1, Options ["*.log"]           -> `'1: :_files -g "*.log"'`
//   file hint,  i=2, no options                  -> `'2: :_files '`
//   word hint,  i=1, Options ["word1","word2"]   -> `'1: :("word1" "word2")'`
// and returns an error ("Invalid zsh argument completion annotation: <type>") for any other Tipe.
func zshCompRenderZshCompArgHint(i int, z zshCompArgHint) (string, error)
```
