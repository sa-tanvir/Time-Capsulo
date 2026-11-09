# Functional specification: `func splitPossiblePipe(path string) (left, right string, ok bool)`

## 1. Component overview

`splitPossiblePipe` is an internal helper of the `gjson` package
(`github.com/tidwall/gjson`). GJSON paths are made of components separated by
`.` (descend) or `|` (pipe: apply the rest of the path to the result so far),
e.g. `info.friends|0|first`. Components may contain queries such as
`#(first=="Dale")` or `#[a|1="x|y"]#` and multipaths such as `{a,b}`, whose
contents may themselves contain `|` characters that must **not** be treated as
pipes. `Get` calls this function to find the first *top-level* pipe of a path and
split the path there into the part before the pipe (`left`) and the part after
it (`right`).

## 2. Functional requirements

1. **Quick exit.** If `path` contains no `|` byte at all, return
   `"", "", false`.
2. **Paths that start with `{`** (a multipath). Let `sq = squash(path[1:])`
   (the `squash` helper from the context, applied to the text after the
   leading `{`; note that `squash` treats the first character of its argument
   as the opening character). If `len(sq) < len(path)-1` and the character of
   `path` at index `len(sq)+1` is `|`, return
   `left = path[:len(sq)+1]`, `right = path[len(sq)+2:]`, `ok = true`.
   Otherwise return `"", "", false`. No other rule is applied to such paths.
3. **All other paths** are scanned from left to right:
   - `\` escapes the next character: the following character is skipped (so
     `\|` is never a pipe).
   - The first unskipped `|` is the split point: return
     `left = path[:i]`, `right = path[i+1:]`, `ok = true` (`i` = index of the
     `|`). `left` and/or `right` may be empty.
   - A `.` that is the **last** character of the path ends the scan with
     `"", "", false`.
   - A `.` immediately followed by `#` introduces an array selector:
     - if the path ends right after the `#`, return `"", "", false`;
     - the character right after `.#` is consumed without being examined (it
       can never be a pipe or an escape), except that
     - if that character is `(` or `[`, the whole bracketed selector is skipped:
       nesting is counted only for that bracket kind (`(`/`)` or `[`/`]`; the
       other kind is ignored), `\` skips the next character, and double-quoted
       strings (with `\` escapes inside them) are skipped so brackets and pipes
       inside them are ignored. Scanning resumes after the matching closing
       bracket. If the selector is never closed, the scan reaches the end.
   - A `#` that is not directly preceded by `.` gets no special treatment (its
     brackets are not skipped).
   - If the end of the path is reached without finding a pipe, return
     `"", "", false`.
4. When `ok` is false, `left` and `right` are always empty strings.
5. Pure; safe for concurrent use.

## 3. Input specification

- `path`: any GJSON path string (possibly empty), arbitrary bytes. A path that
  starts with `{"` always contains the closing quote of that string.

## 4. Output specification

- `(left, right, true)` with `left + "|" + right == path` when a top-level pipe
  is found, otherwise `("", "", false)`.

## 5. Edge cases and constraints

Examples (Go raw-string literals; result shown as `left`, `right`, `ok`):

```
`hello`                                         -> "", "", false
`hello.world`                                   -> "", "", false
`hello|world`                                   -> `hello`, `world`, true
`a|b|c`                                         -> `a`, `b|c`, true
`hello\|world`                                  -> "", "", false   (escaped pipe)
`hello.#`                                       -> "", "", false
`hello.#[a|1="asdf\"|1324"]#\|that`             -> "", "", false
`hello.#[a|1="asdf\"|1324"]#|that.more|yikes`   -> `hello.#[a|1="asdf\"|1324"]#`, `that.more|yikes`, true
`a.#[]#\|b`                                     -> "", "", false
`a.#|b`                                         -> "", "", false   (the char after ".#" is skipped)
`a.#.b|c`                                       -> `a.#.b`, `c`, true
`a.#\|b`                                        -> `a.#\`, `b`, true (the "\" after ".#" is skipped unexamined)
`#(a|b)|c`                                      -> `#(a`, `b)|c`, true (no "." before "#")
`a.#(b|c`                                       -> "", "", false   (selector never closed)
`a.#[x]|y`                                      -> `a.#[x]`, `y`, true
`a.#(b=="x|y")|z`                               -> `a.#(b=="x|y")`, `z`, true
`a.#(b(c)|d)|e`                                 -> `a.#(b(c)|d)`, `e`, true
`a.#[b(c|d]|e`                                  -> `a.#[b(c|d]`, `e`, true
`a.#(b="q\"|")#|c`                              -> `a.#(b="q\"|")#`, `c`, true
`.|x`                                           -> `.`, `x`, true
`a.|b`                                          -> `a.`, `b`, true
`a|`                                            -> `a`, "", true
`|`                                             -> "", "", true
``  (empty)                                     -> "", "", false
`x.#(`                                          -> "", "", false
`{a,b}|c`                                       -> `{a,b}`, `c`, true
`{x.#(a|b)}|c`                                  -> `{x.#(a|b)}`, `c`, true
`{"a":b}|c`                                     -> "", "", false   (squash of `"a":b}|c` is `"a"`)
`{[a]}|x`                                       -> "", "", false   (squash of `[a]}|x` is `[a]`)
`{a|b`                                          -> "", "", false
`{|`                                            -> "", "", false
```

- Must run in time linear in the length of `path`.
