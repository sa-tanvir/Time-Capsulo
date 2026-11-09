You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func zshCompGenFlagEntryExtras(f *pflag.Flag) string`

## 1. Component overview

Package `cobra` (`github.com/spf13/cobra`) generates zsh completion scripts.
Every visible flag of a command becomes one entry of zsh's `_arguments`
builtin, e.g. `'--config[config file]:filename:_files'`. The part after the
closing `]` describes whether the flag takes a value and how that value is
completed. `zshCompGenFlagEntryExtras` computes exactly this trailing part
for a single flag, based on the flag's `NoOptDefVal` and its completion
annotations (`f.Annotations`).

## 2. Functional requirements

1. If `f.NoOptDefVal` is non-empty (the flag can be given without a value,
   e.g. every boolean flag, whose `NoOptDefVal` is `"true"`), return the
   empty string `""`. Annotations are ignored in this case.
2. Otherwise the default result is `":"` (the flag takes a value, without
   completion assistance).
3. Annotation keys other than the two listed below are ignored.
4. If `f.Annotations` has the key `BashCompFilenameExt` (set by
   `MarkFlagFilename`) with a list of patterns, the result is
   `":filename:_files"` followed, for each pattern `p` in list order, by
   ` -g "p"` (a space, `-g`, a space, then `p` verbatim inside double quotes,
   without escaping).
   - patterns `[]` → `":filename:_files"`
   - patterns `["*.log","*.txt"]` → `":filename:_files -g \"*.log\" -g \"*.txt\""`,
     i.e. the text `:filename:_files -g "*.log" -g "*.txt"`.
5. If `f.Annotations` has the key `zshCompDirname` (set by `MarkFlagDirname`),
   the result is `":filename:_files -g "` followed by the **first** element of
   that annotation's list rendered as a Go double-quoted literal, as produced by
   `fmt.Sprintf("%q", v)`. Only the first element is used.
   - `["-(/)"]` → the text `:filename:_files -g "-(/)"`
6. The function never modifies the flag.

Examples (`NoOptDefVal`, `Annotations` → result text):

| NoOptDefVal | Annotations | result |
|---|---|---|
| `"true"` | none | `` (empty) |
| `"true"` | `{BashCompFilenameExt: ["*.go"]}` | `` (empty) |
| `""` | none / nil | `:` |
| `""` | `{"other": ["x"]}` | `:` |
| `""` | `{BashCompFilenameExt: []}` | `:filename:_files` |
| `""` | `{BashCompFilenameExt: ["*.log","*.txt"]}` | `:filename:_files -g "*.log" -g "*.txt"` |
| `""` | `{zshCompDirname: ["-(/)"]}` | `:filename:_files -g "-(/)"` |
| `""` | `{zshCompDirname: ["a\"b", "ignored"]}` | `:filename:_files -g "a\"b"` |

## 3. Input specification

- `f`: a non-nil `*pflag.Flag`. Only `f.NoOptDefVal` and `f.Annotations` are
  relevant. `f.Annotations` may be nil, empty, or contain arbitrary other keys.
- When the `zshCompDirname` key is present its list has at least one element.
- A flag never carries both the `zshCompDirname` and the
  `BashCompFilenameExt` annotation at the same time (the result for that
  combination is unspecified).

## 4. Output specification

- A `string`: `""`, `":"`, or a text starting with `":filename:_files"` as
  described above.

## 5. Edge cases and constraints

- Non-empty `NoOptDefVal` always wins: result `""`.
- Empty pattern list for `BashCompFilenameExt` gives `":filename:_files"`
  with no trailing space.
- Patterns are inserted verbatim (no escaping) for `BashCompFilenameExt`,
  but the directory value is Go-quoted for `zshCompDirname`.
- Pure function; no errors; never panics for valid input.

=== CONTEXT ===
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

=== STUB ===
```go
func zshCompGenFlagEntryExtras(f *pflag.Flag) string {
    // TODO: implement according to the specification
}
```
