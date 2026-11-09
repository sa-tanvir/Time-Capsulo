You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func tostr(json string) (raw string, str string)`

## 1. Component overview

`tostr` is an internal helper of the `gjson` package (`github.com/tidwall/gjson`),
which extracts values from JSON text without fully decoding it. It is called when
the parser reaches a JSON string literal: `json` is the remainder of a document,
starting at the opening `"`. `tostr` returns the raw text of the literal (as it
appears in the document) and its decoded value. `Parse` and the array/object
member listing (`Result.Array`, `Result.Map`, `Result.Value`) use it to fill in
`Result.Raw` and `Result.Str` for string values.

## 2. Functional requirements

Let the *closing quote* be the first `"` after the opening one that is preceded
by an **even** number (including zero) of consecutive backslashes. (A quote
preceded by an odd number of backslashes is escaped and belongs to the string.)

1. **No backslash before the closing quote.** If a closing quote is found and
   there is no `\` between the opening and the closing quote:
   - `raw` = the input up to and including the closing quote;
   - `str` = the characters between the two quotes, copied **verbatim** (no
     decoding; control characters such as a literal tab are kept).
2. **No backslash and no closing quote.** `raw` = the whole input and `str` =
   the whole input without its first character.
3. **Backslash present.** If a `\` occurs before the closing quote (or before
   the end of the input when there is no closing quote):
   - Let `end` be the index of the closing quote, or `len(json)` when there is
     none.
   - `str` = `unescape(json[1:end])`, i.e. the content between the opening quote
     and `end`, decoded exactly as the `unescape` function in the context does
     (decoding stops early at a raw control character, an unknown escape, or a
     truncated `\u` escape).
   - `raw` = `json[:end+1]` (through the closing quote) **if** there is at least
     one more character after the closing quote; otherwise (the closing quote is
     the very last character of the input, or there is no closing quote)
     `raw` = `json[:end]`. In other words, in the escaped case a closing quote
     that ends the input is *not* included in `raw`.
4. Text after the closing quote is ignored. The function is pure and safe for
   concurrent use; it never panics for inputs that meet section 3.

## 3. Input specification

- `json`: a Go string of length >= 1 whose first byte is `"`. The rest is
  arbitrary bytes (normally JSON string content, possibly with `\uXXXX`
  escapes, raw UTF-8, and trailing document text such as `,`, `]`, `}`).

## 4. Output specification

- `raw`: always a prefix of `json` (starting with the opening quote).
- `str`: the decoded string value as described above (valid or invalid UTF-8
  is passed through unchanged in the verbatim case; `\u` escapes are encoded as
  UTF-8, lone surrogates become U+FFFD as done by `unescape`).

## 5. Edge cases and constraints

Inputs and outputs below are shown as raw text; `<TAB>` is a literal tab byte.

| `json` | `raw` | `str` |
|---|---|---|
| `"hello"` | `"hello"` | `hello` |
| `"hello",1` | `"hello"` | `hello` |
| `""` | `""` | (empty) |
| `"",` | `""` | (empty) |
| `"abc` | `"abc` | `abc` |
| `"a<TAB>b"x` | `"a<TAB>b"` | `a<TAB>b` |
| `"中文",` | `"中文"` | `中文` |
| `"a\"b",` | `"a\"b"` | `a"b` |
| `"a\"b"` | `"a\"b` (final quote dropped) | `a"b` |
| `"\\"x` | `"\\"` | `\` |
| `"x\\\"y"z` | `"x\\\"y"` | `x\"y` |
| `"été"}` | `"été"` | `été` |
| `"😀"]` | `"😀"` | `😀` |
| `"\ud83d"]` | `"\ud83d"` | U+FFFD |
| `"\/\b\f\r\t"` | `"\/\b\f\r\t` | `/`, backspace, form feed, CR, tab |
| `"ab\ncd` | `"ab\ncd` | `ab`, newline, `cd` |
| `"a<TAB>b\n"` | `"a<TAB>b\n` | `a` (decoding stops at the raw tab) |
| `"bad\q"x` | `"bad\q"` | `bad` (unknown escape stops decoding) |
| `"\u12"` | `"\u12` | (empty: truncated `\u` escape) |
| `"\` | `"\` | (empty) |
| `"\"` | `"\"` | `"` (no closing quote) |
| `"q\\"` | `"q\\` | `q\` |

- Runs in time linear in the length of the string literal.

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
splitPossiblePipe path string
squash json string
tolit json string
tonum json string
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

- `unescape(json string) string`: decodes the JSON escape sequences (`\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX` incl. surrogate pairs) of a string body (the text between the quotes) and returns the decoded string.

=== STUB ===
```go
func tostr(json string) (raw string, str string) {
    // TODO: implement according to the specification
}
```
