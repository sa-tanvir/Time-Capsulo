You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func parseArrayPath(path string) (r arrayPathResult)`

## 1. Component overview

`parseArrayPath` is an internal helper of the `gjson` package
(`github.com/tidwall/gjson`). `Get(json, path)` walks a JSON document following
a dot/pipe separated path such as `friends.#(last=="Murphy")#.first`,
`items.3.tags.#` or `programmers.#.firstName`. When the walk is positioned on a
JSON **array**, `parseArrayPath` is called with the remaining path. It splits
off the first path component and classifies it, returning an `arrayPathResult`
(the struct is defined in the context). The array walker then uses that
description: a numeric index (`3`), `#` (count), `#.key` (collect `key` from
every element), or a query `#(...)` / `#[...]`, optionally followed by `#`
(return all matches instead of the first).

## 2. Functional requirements

Start from the zero `arrayPathResult` and scan `path` from left to right. The
first component ends at the first `.` or `|` that is reached by the scan
(characters consumed as part of a query, see rule 4, are not examined).
There is **no** backslash escaping in this function (`a\.b` splits after
`a\`).

1. **`|` ends the component:** `part` = text before it, `pipe` = text after it,
   `piped = true`; stop.
2. **`.` ends the component:** `part` = text before it, `path` = text after it,
   `more = true`; stop.
3. **`#` anywhere** sets `arrch = true` and scanning continues.
4. **`#` at index 0 with at least one more character** additionally:
   - if the next character is `.`: `alogok = true` and `alogkey` = everything
     after `#.` (the rest of the whole path). Scanning then reaches the `.` at
     index 1, so `part = "#"`, `path` = everything after `#.`, `more = true`.
   - if the next character is `(` or `[`: this is a query; set
     `query.on = true` and parse it with `parseQuery(path)` (context helper).
     - If `parseQuery` fails (`ok == false`), scanning stops immediately and
       the end-of-input rule (6) applies: `part` = the whole path. Only
       `arrch` and `query.on` are set; the other query fields stay empty.
     - Otherwise `query.path`, `query.op` and `query.value` are set to the
       `path`, `op` and `value` returned by `parseQuery`, and scanning resumes
       at the index it returned (just after the closing bracket), so `.` and
       `|` inside the query are never separators. If the character at that
       index is `#`, `query.all = true` (that `#` is then scanned normally).
   - any other next character: nothing extra.
5. A `#` at an index other than 0, or a `(`/`[` not directly after a leading
   `#`, has no further meaning (only rule 3 applies).
6. **End of input** without a separator: `part` = the whole path, `path` = `""`,
   `more` and `piped` false.
7. Fields not mentioned stay at their zero values. Pure; safe for concurrent
   use.

## 3. Input specification

- `path`: any Go string (possibly empty, arbitrary bytes): the remaining GJSON
  path at an array.

## 4. Output specification

- An `arrayPathResult` value with fields `part`, `path`, `pipe`, `piped`,
  `more`, `alogok`, `arrch`, `alogkey`, and `query.{on, path, op, value, all}`
  as described. All string fields are substrings of the input or results of
  `parseQuery`.

## 5. Edge cases and constraints

Each line: input (Go raw string) -> the non-zero fields.

```
``                     -> (all zero)
`abc`                  -> part=`abc`
`0.1`                  -> part=`0` path=`1` more
`a|b`                  -> part=`a` pipe=`b` piped
`.a`                   -> part=`` path=`a` more
`|a`                   -> part=`` pipe=`a` piped
`a\.b.c`               -> part=`a\` path=`b.c` more
`a.#(b=1)`             -> part=`a` path=`#(b=1)` more            (query not at index 0 of this call)
`#`                    -> part=`#` arrch
`##`                   -> part=`##` arrch
`#x.y`                 -> part=`#x` path=`y` more arrch
`a#b.c`                -> part=`a#b` path=`c` more arrch
`#|x`                  -> part=`#` pipe=`x` piped arrch
`#.`                   -> part=`#` path=`` more alogok arrch alogkey=``
`#.name.first`         -> part=`#` path=`name.first` more alogok arrch alogkey=`name.first`
`#.#.a`                -> part=`#` path=`#.a` more alogok arrch alogkey=`#.a`
`#.|x`                 -> part=`#` path=`|x` more alogok arrch alogkey=`|x`
`#(a=1)`               -> part=`#(a=1)` arrch q.on q.path=`a` q.op=`=` q.value=`1`
`#(a=1)#`              -> part=`#(a=1)#` arrch q.on q.path=`a` q.op=`=` q.value=`1` q.all
`#(a=1)#.b`            -> part=`#(a=1)#` path=`b` more arrch q.on a,=,1 q.all
`#(a=1).b`             -> part=`#(a=1)` path=`b` more arrch q.on a,=,1
`#(a=1)|b`             -> part=`#(a=1)` pipe=`b` piped arrch q.on a,=,1
`#(a=1)#|#`            -> part=`#(a=1)#` pipe=`#` piped arrch q.on a,=,1 q.all
`#[first%"D*"]#.last`  -> part=`#[first%"D*"]#` path=`last` more arrch q.on q.path=`first` q.op=`%` q.value=`"D*"` q.all
`#(a="x.y|z")#.c`      -> part=`#(a="x.y|z")#` path=`c` more arrch q.on a,=,`"x.y|z"` q.all
`#(service_roles.#(=="one"))#.v`
                       -> part=`#(service_roles.#(=="one"))#` path=`v` more arrch q.on q.path=`service_roles.#(=="one")` q.op=`` q.value=`` q.all
`#( a > 5 )`           -> part=`#( a > 5 )` arrch q.on q.path=`a` q.op=`>` q.value=`5`
`#(a)`                 -> part=`#(a)` arrch q.on q.path=`a`
`#()`                  -> part=`#()` arrch q.on
`#[]#`                 -> part=`#[]#` arrch q.on q.all
`#(a!b)`               -> part=`#(a!b)` arrch q.on q.path=`a` q.op=`` q.value=`!b`
`#(b(c)=1)rest.x`      -> part=`#(b(c)=1)rest` path=`x` more arrch q.on q.path=`b(c)` q.op=`=` q.value=`1`
`#(a=1)x#.y`           -> part=`#(a=1)x#` path=`y` more arrch q.on a,=,1      (q.all false: no `#` right after `)`)
`#(a=1)#x.y`           -> part=`#(a=1)#x` path=`y` more arrch q.on a,=,1 q.all
`#(a`                  -> part=`#(a` arrch q.on                    (bad query)
`#(a.b`                -> part=`#(a.b` arrch q.on                  (bad query: no split at the `.`)
`##(a=1)`              -> part=`##(a=1)` arrch                     (not a query)
```

- Must run in time linear in the length of the first component (including a
  leading query).

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

=== STUB ===
```go
func parseArrayPath(path string) (r arrayPathResult) {
    // TODO: implement according to the specification
}
```
