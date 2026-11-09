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

- `(t Result) Exists() bool`: true when `t.Type != Null || len(t.Raw) != 0` (a json `null` exists; the zero `Result{}` does not).
- `parseString(json string, i int) (next int, raw string, escaped bool, ok bool)`: `json[i-1]` is an opening `"`. Finds the closing quote (a `"` preceded by an even number of consecutive backslashes). On success returns the index just after the closing quote, `raw = json[i-1:next]` (quotes included), whether the string contains any backslash, and `ok = true`. If there is no closing quote, `ok` is false.
- `parseAny(json string, i int, hit bool) (next int, res Result, ok bool)`: starting at index `i`, skips every byte that cannot start a value (anything other than `"`, `-`, a digit, `t`, `f`, `n`, `{`, `[`; so whitespace, `,`, `:`, `]`, `}` and other text are all skipped) and parses the first value found, returning the index just after it and `ok = true`. With `hit = true`, `res` is filled in (`Index` is left 0): a string gives Type String, Raw = quoted text, Str = decoded content (as by `unescape` when the string contains backslashes); a number (starting with `-` or a digit) gives Type Number, Raw = text up to the next whitespace, `,`, `]` or `}`, Num = `strconv.ParseFloat(Raw, 64)` (error ignored); `t`/`f`/`n` give Type True/False/Null with Raw = the run of lowercase letters (`true`, `false`, `null`); `{`/`[` give Type JSON with Raw = the balanced text of that object/array. `ok` is false when no value is found before the end of `json` or a string is not terminated.
- `unescape(json string) string`: decodes the JSON escape sequences (`\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX` incl. surrogate pairs) of a string body (the text between the quotes) and returns the decoded string.
