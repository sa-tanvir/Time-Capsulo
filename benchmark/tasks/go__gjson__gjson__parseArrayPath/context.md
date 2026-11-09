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
// arrayPathResult describes the first component of a path that is applied to a JSON array.
type arrayPathResult struct {
	part    string // the first path component
	path    string // the rest of the path after a '.' separator
	pipe    string // the rest of the path after a '|' separator
	piped   bool   // true when the component was terminated by '|'
	more    bool   // true when the component was terminated by '.'
	alogok  bool   // true for a "#.key" component (collect "key" from every element)
	arrch   bool   // true when the component contains a '#'
	alogkey string // the key that follows "#."
	query   struct {
		on    bool   // the component is a "#(...)" / "#[...]" query
		path  string // the query's left-hand path
		op    string // the comparison operator ("" = existence test)
		value string // the query's right-hand value (still quoted if it was a string)
		all   bool   // the query is followed by '#' (return all matches)
	}
}
```

## Behaviour of helpers used by the original implementation (you may call them)

- `parseQuery(query string) (path, op, value, remain string, i int, ok bool)`: parses a query that starts at the beginning of `query` in the form `#(...)` or `#[...]`. On success `ok` is true, `path` is the trimmed left-hand path, `op` the comparison operator (`=`, `!=`, `<`, `<=`, `>`, `>=`, `%`, `!%`, or `""` for an existence test; `==` is reported as `=`), `value` the trimmed right-hand side (quotes kept), `remain` the text after the closing bracket, and `i` the index just after the closing bracket. `ok` is false when `query` does not start with `#(`/`#[` or the brackets are not balanced.
