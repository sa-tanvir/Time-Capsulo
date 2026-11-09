You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func parseQuery(query string) (path, op, value, remain string, i int, ok bool)`

## 1. Component overview

`parseQuery` is an internal helper of the `gjson` package
(`github.com/tidwall/gjson`). GJSON paths can filter arrays with queries such as
`friends.#(last=="Murphy").first`, `friends.#(age>45)#.last`,
`#[first%"D*"]` or nested ones like
`instances.#(service_roles.#(=="one"))#.service_version`. A query starts with
`#(` (or the older `#[`) and ends at the matching closing bracket. Inside it
there is a left-hand *path*, optionally followed by a comparison *operator* and
a right-hand *value*; without an operator the query only tests that the path
exists.

`parseQuery` takes a string that starts with such a query, splits the query
into `path`, `op` and `value`, and also reports the text that follows the
query (`remain`) and the index just after the closing bracket (`i`).

## 2. Functional requirements

1. **Recognition.** If `query` is shorter than 2 bytes, or does not start with
   `#(` or `#[`, return `ok = false`.
2. **Finding the end of the query.** Scan from index 2 with a nesting depth of
   1:
   - `\` skips the next character (it never opens/closes anything and is never
     an operator);
   - `(` or `[` increases the depth; `)` or `]` decreases it (kinds are not
     matched: `#(a]` is a complete query). When the depth reaches 0, that
     character is the closing bracket;
   - `"` starts a quoted string that runs to the next unescaped `"` (inside it,
     `\` skips the next character); brackets inside it are ignored.
   If the input ends before the depth reaches 0, return `ok = false`.
3. **Operator start.** While scanning at depth 1 and before any operator start
   has been found, the first character among `!`, `=`, `<`, `>`, `%` (not
   inside a quoted string, not escaped) marks the start of the operator.
   Characters inside nested brackets or quoted strings never mark it.
4. **Without an operator:** `path` = the text between `#(` and the closing
   bracket, trimmed; `op` = `""`; `value` = `""`.
5. **With an operator:** `path` = the text between `#(` and the operator start,
   trimmed. Let `v` = the text from the operator start up to (not including)
   the closing bracket, trimmed. The operator is the longest match at the start
   of `v`:
   - if `v` is exactly one character, that character is the operator and the
     value is empty;
   - two-character operators: `!=`, `!%`, `<=`, `>=`;
   - `==` is reported as `=` (the operator is `=`, the value is what follows
     `==`);
   - one-character operators: `<`, `>`, `=`, `%`;
   - otherwise (e.g. `!` followed by anything other than `=`/`%`) the operator
     is empty and the whole of `v` is the value.
   `value` = the rest of `v` after the operator, trimmed again. Quotes around
   the value are kept (`"Murphy"` stays `"Murphy"`).
   "Trimmed" means: leading and trailing bytes `<= ' '` (space, tab, newline,
   other control bytes) removed (the `trim` helper).
6. **Results on success:** `remain` = everything after the closing bracket
   (e.g. `.last`, `#.name`, `|#`), `i` = index of the closing bracket + 1, and
   `ok = true`.
7. **Failure:** when `ok` is false, `path`, `op`, `value` and `remain` are all
   `""`; the value of `i` is not specified (callers ignore it).
8. Pure; safe for concurrent use. No unescaping is done: all parts are
   substrings of the input (after trimming).

## 3. Input specification

- `query`: any Go string (possibly empty, arbitrary bytes), normally the part
  of a GJSON path that starts at a `#(` / `#[` query.

## 4. Output specification

- `path`, `op`, `value`, `remain` (strings), `i` (int), `ok` (bool) as above.
  `op` is always one of `""`, `=`, `!=`, `<`, `<=`, `>`, `>=`, `%`, `!%`.

## 5. Edge cases and constraints

Each line: input (Go raw string) -> `ok`, `path`, `op`, `value`, `remain`, `i`.

```
`#(service_roles.#(=="one").()==asdf).cap` -> true `service_roles.#(=="one").()` `=` `asdf` `.cap` 36
`#(first_name%"Murphy").last`              -> true `first_name` `%` `"Murphy"` `.last` 22
`#( first_name !% "Murphy" ).last`         -> true `first_name` `!%` `"Murphy"` `.last` 27
`#(service_roles.#(=="one"))`              -> true `service_roles.#(=="one")` `` `` `` 27
`#(a\("\"(".#(=="o\"(ne")%"ab\")").remain` -> true `a\("\"(".#(=="o\"(ne")` `%` `"ab\")"` `.remain` 33
`#[age=101].x`                             -> true `age` `=` `101` `.x` 10
`#(  a  ==  "b"  )rest`                    -> true `a` `=` `"b"` `rest` 17
`#(a>=1)#`                                 -> true `a` `>=` `1` `#` 7
`#[a%"x*"]#.b`                             -> true `a` `%` `"x*"` `#.b` 9
`#(a>"(")x`                                -> true `a` `>` `"("` `x` 8
`#(a=[1,2])`                               -> true `a` `=` `[1,2]` `` 10
`#(a.#(b=1)=2)`                            -> true `a.#(b=1)` `=` `2` `` 13
`#(a!b)`                                   -> true `a` `` `!b` `` 6
`#(a=!=b)`                                 -> true `a` `=` `!=b` `` 8
`#(a=)`  -> true `a` `=` `` `` 5          `#(a==)` -> true `a` `=` `` `` 6
`#(a!=)` -> true `a` `!=` `` `` 6         `#(a<)`  -> true `a` `<` `` `` 5
`#(=)`   -> true `` `=` `` `` 4           `#(!=1)` -> true `` `!=` `1` `` 6
`#(%"j*")` -> true `` `%` `"j*"` `` 8
`#()`    -> true `` `` `` `` 3            `#[]#|#` -> true `` `` `` `#|#` 3
`#(a]`   -> true `a` `` `` `` 4           `#(a=1)]` -> true `a` `=` `1` `]` 6
```

A tab/newline around the operator or value is trimmed like a space:
`#(a<TAB>=<TAB>true<LF>)` gives `a`, `=`, `true`.

Failures (`ok = false`): `` (empty), `#`, `(`, `x(a=1)`, `##(a)`, `#(a`
(never closed), `#(a="b)` (the quote is never closed, so the `)` is inside the
string), `#(a\)` (the `)` is escaped).

- Must run in time linear in the length of the query.

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

- `trim(s string) string`: returns `s` with all leading and trailing bytes `<= ' '` (space and ASCII control bytes) removed.

=== STUB ===
```go
func parseQuery(query string) (
	path, op, value, remain string, i int, ok bool,
) {
    // TODO: implement according to the specification
}
```
