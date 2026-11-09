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
