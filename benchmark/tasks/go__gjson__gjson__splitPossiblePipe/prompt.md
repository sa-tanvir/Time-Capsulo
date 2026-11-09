You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `gjson.go`

## Imports / includes available in this file

```
import "encoding/base64"
import "encoding/json"
import "errors"
import "reflect"
import "strconv"
import "strings"
import "sync"
import "sync/atomic"
import "time"
import "unicode/utf16"
import "unicode/utf8"
import "github.com/tidwall/match"
import "github.com/tidwall/pretty"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(t Result)Array
(t Result)Bool
(t Result)Exists
(t Result)Float
(t Result)ForEach iterator func key , value Result bool
(t Result)Get path string
(t Result)Int
(t Result)IsArray
(t Result)IsObject
(t Result)Map
(t Result)String
(t Result)Time
(t Result)Uint
(t Result)Value
(t Result)arrayOrMap vc byte , valueize bool
(t Type)String
ForEachLine json string , iterator func line Result bool
Get json , path string
GetBytes json [ ] byte , path string
Parse json string
ParseBytes json [ ] byte
appendJSONString dst [ ] byte , s string
isSimpleName component string
nameOfLast path string
parseArrayPath path string
parseLiteral json string , i int
parseNumber json string , i int
parseObject c * parseContext , i int , path string
parseObjectPath path string
parseQuery query string
parseSquash json string , i int
parseString json string , i int
parseSubSelectors path string
queryMatches rp * arrayPathResult , value Result
runeit json string
squash json string
tolit json string
tonum json string
tostr json string
trim s string
unescape json string
```

## Package-level types (`gjson.go`)

```go
// Type is Result type
type Type int

const (
	Null   Type = iota // 0: a json null (also the zero value: "no result")
	False              // 1: a json false boolean
	Number             // 2: a json number
	String             // 3: a json string
	True               // 4: a json true boolean
	JSON               // 5: a raw block of JSON (object or array)
)

// Result represents a json value.
type Result struct {
	Type  Type    // the json type
	Raw   string  // the raw json text of the value
	Str   string  // the (unescaped) string value, for String results
	Num   float64 // the numeric value, for Number results
	Index int     // index of Raw in the original json; zero means unknown
}
```

## Behaviour of helpers used by the original implementation (you may call them)

- `squash(json string) string`: requires `len(json) >= 1`. Returns the prefix of `json` that holds one bracketed value or string, or `json` unchanged if that value never ends. If `json[0]` is `"`, the result runs through the matching closing quote (a `"` preceded by an even number of consecutive backslashes). Otherwise `json[0]` is treated as an opening bracket **whatever byte it is** (e.g. `squash("a,b}|c") == "a,b}"`), giving nesting depth 1, and scanning starts at `json[1]`: any of `[{(` increases the depth, any of `]})` decreases it (the kinds need not match), double-quoted strings (with backslash escapes) are skipped so brackets inside them are ignored, and the result ends at the byte where the depth returns to 0. Examples: `squash("[a]}|x") == "[a]"`, `squash("\"a\":b}") == "\"a\""`, `squash("(a") == "(a"`.

=== STUB ===
```go
func splitPossiblePipe(path string) (left, right string, ok bool) {
    // TODO: implement according to the specification
}
```
