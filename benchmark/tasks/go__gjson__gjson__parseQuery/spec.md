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
