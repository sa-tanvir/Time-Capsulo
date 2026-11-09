# Functional specification: `func zshCompRenderZshCompArgHint(i int, z zshCompArgHint) (string, error)`

## 1. Component overview

Package `cobra` (`github.com/spf13/cobra`) can generate a zsh completion
script for a command tree (`Command.GenZshCompletion`). Positional arguments
of a command can be annotated with a completion hint (see
`MarkZshCompPositionalArgumentFile` / `MarkZshCompPositionalArgumentWords`
and the types in the context). `zshCompRenderZshCompArgHint` turns **one**
such hint, for positional argument number `i`, into the single-quoted argument
specification that is passed to zsh's `_arguments` builtin in the generated
script.

## 2. Functional requirements

The result depends on `z.Tipe`:

1. **File completion** (`z.Tipe == zshCompArgumentFilenameComp`): `z.Options`
   are glob patterns. Each pattern `g` is rendered as `-g "g"` (the pattern
   inserted verbatim between double quotes, with no escaping). The rendered
   patterns are joined with single spaces, in the order given. The result is
   `'` + decimal `i` + `: :_files ` + joined patterns + `'`.
   Note the space after `_files` is always present, even with no patterns.
   - `i=1, Options=["*.log"]` → `'1: :_files -g "*.log"'`
   - `i=2, Options=[]` (or nil) → `'2: :_files '`
   - `i=3, Options=["*.txt","*.md"]` → `'3: :_files -g "*.txt" -g "*.md"'`
2. **Word completion** (`z.Tipe == zshCompArgumentWordComp`): `z.Options` are
   the words. Each word is rendered as a Go double-quoted string literal,
   exactly as produced by `fmt.Sprintf("%q", word)` (so `"` and `\` are
   backslash-escaped, non-printable characters are escaped, and spaces are kept
   inside the quotes). The rendered words are joined with single spaces, in
   the order given. The result is `'` + decimal `i` + `: :(` + joined words +
   `)'`.
   - `i=1, Options=["word1","word2"]` → `'1: :("word1" "word2")'`
   - `i=1, Options=["single","multiple words"]` → `'1: :("single" "multiple words")'`
   - `i=4, Options=["a\"b"]` → `'4: :("a\"b")'`
   - `i=1, Options=[]` → `'1: :()'`
3. **Any other `Tipe`** (including `""` and `zshCompDirname`): return the
   empty string and a non-nil `error` whose message is
   `Invalid zsh argument completion annotation: <Tipe>`.
4. `i` is printed in base 10 as given (it is not validated; `0` and negative
   values are printed as-is).
5. On success the returned error is `nil`. The function has no side effects
   and does not modify `z.Options`.

## 3. Input specification

- `i`: the 1-based positional-argument index (normally `>= 1`).
- `z`: a `zshCompArgHint` value; `z.Options` may be nil or empty and may
  contain any strings (spaces, quotes, non-ASCII).

## 4. Output specification

- `(string, nil)` on success, formatted as described above, always starting
  and ending with a single quote `'`.
- `("", error)` for an unknown `Tipe`.

## 5. Edge cases and constraints

- Empty option list: file → `'N: :_files '` (trailing space before the
  closing quote); words → `'N: :()'`.
- File globs are not escaped; word options are Go-quoted.
- Never panics.
