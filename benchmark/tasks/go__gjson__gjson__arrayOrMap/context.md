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

```go
// arrayOrMapResult holds the members of a JSON array or object.
type arrayOrMapResult struct {
	a  []Result               // array members as Results
	ai []interface{}          // array members as Go values
	o  map[string]Result      // object members as Results
	oi map[string]interface{} // object members as Go values
	vc byte                   // '[' or '{': the container kind that was read
}
```

## Behaviour of helpers used by the original implementation (you may call them)

- `tonum(json string) (raw string, num float64)`: `json` starts with a number (`-` or a digit). `raw` is the number token: the prefix that ends before the first byte (after the first byte) that is whitespace/control (`<= ' '`), `,`, or `>= ']'` other than `e`/`E` (e.g. `]`, `}`); `num` is `strconv.ParseFloat(raw, 64)` (error ignored).
- `tolit(json string) string`: returns the first byte of `json` followed by the run of lowercase ASCII letters `a`-`z` after it (e.g. `"true,1"` gives `"true"`).
- `tostr(json string) (raw string, str string)`: `json` starts with `"`. `raw` is the quoted string token, `str` is its decoded content (escape sequences decoded as by `unescape`).
- `squash(json string) string`: `json` starts with `[`, `{`, `(` or `"`. Returns the prefix of `json` that holds that one value: for `"`, everything through the closing (unescaped) quote; for an opening bracket, everything through the bracket where the nesting depth (any of `[{(` opens, any of `]})` closes, brackets inside quoted strings ignored) returns to zero. If the brackets never close, `json` is returned unchanged.
- `(t Result) Value() interface{}`: converts a Result to a Go value: String -> `string` (`t.Str`), Number -> `float64` (`t.Num`), True/False -> `bool`, Null -> `nil`; JSON -> the `oi` (`map[string]interface{}`) or `ai` (`[]interface{}`) field of `t.arrayOrMap(0, true)` according to its `vc` (`nil` if `vc` is neither `{` nor `[`).
