You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func zshCompExtractArgumentCompletionHintsForRendering(c *Command) ([]string, error)`

## 1. Component overview

Package `cobra` (`github.com/spf13/cobra`) generates zsh completion scripts
(`Command.GenZshCompletion`). For a leaf command the script contains an
`_arguments` call listing the flags and then one specification per
positional argument, such as `'1: :("word1" "word2")'` or
`'2: :_files -g "*.log"'`. This function collects those positional-argument
specifications for command `c`; the zsh template prints them one per line, in
the returned order.

Positional-argument hints are stored on the command as JSON in
`c.Annotations[zshCompArgumentAnnotation]` (written by
`MarkZshCompPositionalArgumentFile` / `MarkZshCompPositionalArgumentWords`).
In addition, a command's `ValidArgs` act as a word-completion hint for the
first positional argument when no explicit hint exists for position 1.

## 2. Functional requirements

1. Decode the stored hints of `c` with `c.zshCompGetArgsAnnotations()`. If
   that fails (the annotation value is not valid JSON for the expected shape),
   return `nil` and that error.
2. Render every stored hint `(position, hint)` with
   `zshCompRenderZshCompArgHint(position, hint)`. If any rendering fails
   (unknown hint type), return `nil` and that error.
3. If `c.ValidArgs` is non-empty **and** there is no stored hint for position
   `1`, additionally produce the rendering of a word-completion hint
   (`Tipe: zshCompArgumentWordComp`) at position `1` whose options are
   `c.ValidArgs` (in their given order). If a hint for position 1 exists,
   `ValidArgs` is ignored.
4. Return all rendered strings **sorted in ascending lexicographic (byte-wise
   string) order**, with a `nil` error. Note this is plain string ordering,
   not numeric: `'10: ...'` sorts before `'2: ...'`.
5. When there is nothing to render (no stored hints and no `ValidArgs`), the
   result is an empty slice (a `nil` slice is acceptable) and a `nil` error.
6. The function does not modify `c` (neither `Annotations` nor `ValidArgs`).

Examples (hints given as position → (type, options)):

| stored hints | `ValidArgs` | result |
|---|---|---|
| none | none | `[]` |
| 1 → file `["*.log"]`, 2 → file `[]` | none | `['1: :_files -g "*.log"'`, `'2: :_files '`] |
| 1 → words `["word1","word2"]` | none | [`'1: :("word1" "word2")'`] |
| none | `["word1","word2"]` | [`'1: :("word1" "word2")'`] |
| 2 → file `[]` | `["word1","word2"]` | [`'1: :("word1" "word2")'`, `'2: :_files '`] |
| 1 → file `["*.txt"]` | `["a"]` | [`'1: :_files -g "*.txt"'`] |
| 2 → words `["x"]`, 10 → file `[]` | none | [`'10: :_files '`, `'2: :("x")'`] |
| 3 → type `"bogus"` | any | error |
| annotation value `"not json"` | any | error |

## 3. Input specification

- `c`: a non-nil `*Command`. Relevant state: `c.Annotations` (may be nil, may
  lack the zsh key, or hold a JSON object mapping position numbers to
  `{"type": ..., "options": [...]}`), and `c.ValidArgs` (may be nil/empty).

## 4. Output specification

- On success: `([]string, nil)`, one entry per stored hint plus possibly one
  for `ValidArgs`, sorted ascending.
- On failure: `(nil, error)` where the error is the one returned by the
  decoding or rendering helper.

## 5. Edge cases and constraints

- The result order must not depend on map iteration order: always sort.
- A stored hint at position 1 always takes precedence over `ValidArgs`.
- Read-only with respect to `c`; safe to call repeatedly with identical results.

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

=== STUB ===
```go
func zshCompExtractArgumentCompletionHintsForRendering(c *Command) ([]string, error) {
    // TODO: implement according to the specification
}
```
