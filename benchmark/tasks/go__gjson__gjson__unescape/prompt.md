You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func unescape(json string) string`

## 1. Component overview

`unescape` is an internal helper of the `gjson` package (`github.com/tidwall/gjson`),
which extracts values from JSON text. When a JSON string literal contains
backslash escape sequences, the library passes the literal's body (the text
between the opening and the closing quote, quotes excluded) to `unescape` to get
the decoded Go string that ends up in `Result.Str` (and in object keys). It must
be lenient: malformed input never causes a panic; decoding simply stops.

## 2. Functional requirements

The input is processed left to right, appending to the output:

1. **Ordinary bytes.** Every byte `>= 0x20` (space) that is not a backslash is
   copied unchanged. This includes `"`, `/`, DEL (0x7F) and every byte of
   multi-byte UTF-8 sequences (raw UTF-8 passes through untouched, valid or
   not).
2. **Raw control bytes stop decoding.** On a byte `< 0x20` (e.g. a literal
   newline, tab or NUL), return the output produced so far; the rest is
   dropped.
3. **Simple escapes.** A backslash followed by one of these characters appends:
   `\\` -> `\`, `\/` -> `/`, `\"` -> `"`, `\b` -> 0x08, `\f` -> 0x0C,
   `\n` -> 0x0A, `\r` -> 0x0D, `\t` -> 0x09.
4. **Unknown or truncated escapes stop decoding.** A backslash that is the last
   byte, or that is followed by any other character (e.g. `\x`, `\q`, `\'`),
   ends decoding: return the output so far (the backslash and everything after
   it are dropped).
5. **`\u` escapes.** `\u` must be followed by at least 4 more bytes; if fewer
   than 4 bytes remain after the `u`, decoding stops (return the output so
   far). Otherwise those 4 bytes are read as a hexadecimal code unit
   (upper- or lower-case digits). If they are not 4 valid hex digits, the code
   unit is 0 (U+0000). Then:
   - If the code unit is a UTF-16 surrogate (0xD800–0xDFFF) **and** the next
     6 bytes exist and start with `\u`, those 6 bytes are consumed as a second
     code unit (again 0 if not valid hex), and the pair is combined as a UTF-16
     surrogate pair. If the two do not form a valid high+low pair (e.g. the
     first is a low surrogate, or the second is not a low surrogate), the
     result is a single U+FFFD and **both** escapes are still consumed.
   - A surrogate that is not followed by at least 6 bytes starting with `\u`
     becomes U+FFFD on its own; nothing after it is consumed and the following
     text is processed normally (e.g. `\ud83dabc` and `\ud83dA`).
   - The resulting code point is appended encoded as UTF-8 (U+0000 is a
     single 0x00 byte).
6. Returns the output as a Go `string`. Pure, no side effects, safe for
   concurrent use.

## 3. Input specification

- `json`: any Go string (possibly empty, arbitrary bytes). Usually the body of a
  JSON string literal, without the surrounding quotes.

## 4. Output specification

- The decoded `string`. Its length never exceeds what the decoded escapes
  produce; for an input without backslashes or control bytes the output equals
  the input.

## 5. Edge cases and constraints

Inputs are shown as raw text (`<NUL>` is a 0x00 byte, `<LF>` a 0x0A byte).

| input | output |
|---|---|
| (empty) | (empty) |
| `plain text` | `plain text` |
| `\\<NUL>` | `\` (the NUL stops decoding) |
| `\/\b\f` | `/`, 0x08, 0x0C |
| `\"quoted\"` | `"quoted"` |
| `tab\there` | `tab`, 0x09, `here` |
| `été` | `été` |
| `中中` | `中中` |
| `😀` | `😀` (U+1F600) |
| `𝄞` | `𝄞` (U+1D11E) |
| `\ud83d` | U+FFFD |
| `\ud83dabc` | U+FFFD then `abc` |
| `\ude00\ud83d` | U+FFFD (one character; both escapes consumed) |
| `\ud83dA` | U+FFFD then `A` (fewer than 6 bytes follow, so nothing extra is consumed) |
| `\ud83d\uzzzz` | U+FFFD |
| `\ud83d\u12` | U+FFFD (then `\u12` is truncated -> stop) |
| `end\ud83d\` | `end` then U+FFFD |
| `\u0000x` | 0x00 then `x` |
| `\uzzzzx` | 0x00 then `x` (invalid hex reads as 0) |
| `\u12`, `\u123` | (empty) |
| `ab\` | `ab` |
| `ab\x` | `ab` |
| `a<LF>b` | `a` |
| `a`, 0x7F, `b` | unchanged (0x7F is not a control byte here) |
| `\\\\` (4 backslashes) | `\\` |

- Must run in time linear in the input length.

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
tostr json string
trim s string
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

- `runeit(json string) rune`: parses the first 4 bytes of `json` as a hexadecimal number and returns it as a rune (0 when those 4 bytes are not valid hex). Requires `len(json) >= 4`.

=== STUB ===
```go
func unescape(json string) string {
    // TODO: implement according to the specification
}
```
