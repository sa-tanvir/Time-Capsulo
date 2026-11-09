You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (t Result) ForEach(iterator func(key, value Result) bool)`

## 1. Component overview

`ForEach` is a public method of `gjson.Result` in the `gjson` package
(`github.com/tidwall/gjson`), a library that reads values out of JSON text
without fully decoding it. A `Result` (see the context) describes one JSON
value; for objects and arrays (`Type == JSON`) `Raw` holds the raw JSON text.
`ForEach` iterates over the members of an object or the elements of an array,
calling `iterator` once per member, in document order, until the iterator
returns `false`. It is used directly by users (e.g.
`gjson.Get(json, "programmers").ForEach(...)`), by `Unmarshal`, and by the
`@reverse` modifier.

Example:
```go
gjson.Parse(`{"name":{"first":"Janet"},"age":47}`).ForEach(func(k, v gjson.Result) bool {
    println(k.String(), v.Raw) // "name" {"first":"Janet"}   then   "age" 47
    return true
})
```

## 2. Functional requirements

1. **Non-existent result.** If `t` does not exist (`t.Type == Null` and
   `t.Raw == ""`, e.g. the zero `Result{}`), `iterator` is never called.
2. **Scalar result.** If `t.Type` is not `JSON` (and `t` exists), call
   `iterator(Result{}, t)` exactly once (passing `t` unchanged) and return,
   regardless of the iterator's return value. A `null` result with
   `Raw == "null"` exists, so it is passed once.
3. **JSON result.** Skip leading whitespace (bytes `<= ' '`) in `t.Raw`. If the
   first other byte is `{` the value is iterated as an object, if it is `[` as
   an array; if it is anything else, or there is none, `iterator` is never
   called.
4. **Arrays.** For each element in order, call `iterator(Result{}, value)`
   (the key is always the zero `Result`).
5. **Objects.** For each member in order, call `iterator(key, value)`, where
   `key` is a `Result` with `Type = String`, `Raw` = the key's raw quoted text
   (e.g. `"asd\nf"` with its escapes), `Str` = the decoded key (escape
   sequences decoded exactly like the `unescape` helper; verbatim when the key
   contains no backslash), `Num = 0`, and `Index` = byte offset of the key's
   opening quote within `t.Raw`. Duplicate keys are all reported, in order.
6. **Member values** (arrays and objects) are `Result`s whose `Index` is the
   byte offset of the value's first byte within `t.Raw` (offsets are relative
   to `t.Raw`, not to `t.Index`), and whose other fields are:
   - string: `Type = String`, `Raw` = the quoted text, `Str` = decoded content
     (as `unescape`; verbatim if no backslash), `Num = 0`;
   - number (starts with `-` or a digit): `Type = Number`, `Raw` = the text up
     to the next whitespace, `,`, `]` or `}`, `Num = strconv.ParseFloat(Raw, 64)`
     with the error ignored (`1e400` gives `+Inf`, `-0` gives negative zero),
     `Str = ""`;
   - `true`/`false`: `Type = True`/`False`, `Raw` = the run of lowercase
     letters starting there (`true`, `false`);
   - `null` (any run of lowercase letters starting with `n`, e.g. `nul`):
     `Type = Null`, `Raw` = that run;
   - object/array: `Type = JSON`, `Raw` = the complete nested text from its
     opening to its matching closing bracket (brackets inside strings
     ignored), `Str = ""`, `Num = 0`.
   This is exactly the `Result` produced by `parseAny(..., true)` (context),
   with `Index` set.
7. **Separators and scanning.** The member list is scanned leniently:
   - Objects: to find each key, every byte up to the next `"` is skipped
     (this includes `,`, `}` and any unquoted text). Unquoted keys are
     therefore not recognised: `{a:1}` gives no calls, and in `{a:"x"}` the
     string `"x"` is taken as a key (no value follows it, so no call). When no
     further `"` exists, iteration ends.
   - Before each value (after a key, or for each array element), whitespace,
     `,` and `:` are skipped; then any bytes that cannot start a value are
     skipped too (a value starts with `"`, `-`, a digit, `t`, `f`, `n`, `{` or
     `[`; so `]` and `}` are skipped as well). If no value start is found
     before the end of `Raw`, iteration ends. Example: `[1, ]` -> one call,
     `[x, 1]` -> one call (`1`).
   - After each value, exactly one byte (normally the following separator or
     the closing bracket) is skipped without being examined.
   - Iteration ends when the end of `Raw` is reached; the closing `]`/`}` is
     not itself a stop marker (for the usual single, well-formed value it is
     the last meaningful byte, so iteration ends there).
8. **Early stop.** As soon as `iterator` returns `false`, `ForEach` returns
   without further calls.
9. **Malformed input never panics.** If a key or string value is not
   terminated, or no value follows a key or a separator, `ForEach` returns silently (members
   already reported stay reported). Text after the last element of an
   unterminated array (e.g. `["x",`) simply ends the iteration.
10. `t` is not modified; `ForEach` itself keeps no state between calls.

## 3. Input specification

- `t`: any `Result`. For `Type == JSON`, `Raw` is normally well-formed JSON text
  of an object or array (members separated by commas), possibly with leading
  whitespace, newlines/tabs, escaped strings and raw UTF-8.
- `iterator`: a non-nil function when it would be called (it may be `nil` when
  `t` produces no calls, e.g. `Result{}` or `Raw == "*invalid*"`).

## 4. Output specification

- No return value; the observable behaviour is the sequence of
  `iterator(key, value)` calls described above.

## 5. Edge cases and constraints

Calls are shown as `(key.Str, value.Raw)`; offsets are the `Index` fields.

- `Result{}` -> no calls. `Result{Type: JSON, Raw: "*invalid*"}`, `Raw: ""`,
  `Raw: "   "` -> no calls.
- `Result{Type: String, Raw: "", Str: "Hello"}` -> one call `(Result{}, t)`.
- `Result{Type: Number, Raw: "12.5", Num: 12.5}` -> one call with `t`.
- `{}`, `[]`, ` [ ] ` -> no calls.
- `{"bad` -> no calls; `{"ok":"bad` -> no calls (value never terminated).
- `[1,2,3,4]` with an iterator that returns false on its 2nd call -> exactly
  two calls (`1`, `2`).
- `[1, "a\"b", {"x":[1]}, true, false, null, -1.5e3, [], {}]` -> nine calls,
  values `1`, `"a\"b"` (Str `a"b`), `{"x":[1]}`, `true`, `false`, `null`
  (Type Null), `-1.5e3` (Num -1500), `[]`, `{}`; the first value has Index 1.
- `{"a" : [1,{"b":"]"}] , "c\"d" : "eé"}` -> keys `a` (Index 1) and `c"d`
  (key Raw `"c\"d"`), values `[1,{"b":"]"}]` and `"eé"` (Str `eé`).
- `{"a":1,"a":2}` -> two calls, both with key `a`.
- `{"k":nul}` -> one call, value Type Null with Raw `nul`.
- `["x",` -> one call (`"x"`).
- `{a:1}`, `{a:"x"}` -> no calls. `[1, ]`, `[x, 1]`, `["a""b"]` -> one call each
  (`1`, `1`, `"a"`). `[1] 2` -> two calls (`1`, `2`): text after the
  closing bracket is still scanned.
- `\n\t[ "中" ,\n 3 ]` -> values `"中"` (Str `中`, Index 4) and `3`.
- Must run in time linear in `len(t.Raw)` (plus the iterator's own cost).

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

=== STUB ===
```go
func (t Result) ForEach(iterator func(key, value Result) bool) {
    // TODO: implement according to the specification
}
```
