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
