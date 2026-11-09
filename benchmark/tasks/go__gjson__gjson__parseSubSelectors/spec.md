# Functional specification: `func parseSubSelectors(path string) (sels []subSelector, out string, ok bool)`

## 1. Component overview

`parseSubSelectors` is an internal helper of the `gjson` package
(`github.com/tidwall/gjson`). GJSON supports *multipaths*: a path component
written as `[path1,path2,...]` builds a new JSON array from several paths, and
`{name1:path1,path2,...}` builds a new JSON object (an element without a name
gets a name derived from its path). For example
`Get(json, "{age,first|@case:upper}|@ugly")` or
`Get(json, "info.friends.[0.first,1.extra.0]")`.

When `Get` reaches a component that starts with `[` or `{`, it calls
`parseSubSelectors` to split the multipath into its elements (each with an
optional explicit name) and to find the text that follows the closing bracket.
The `subSelector` type is defined in the context.

## 2. Functional requirements

The first character of `path` is the opening `[` or `{` and is not examined.
Scanning starts at index 1 with a nesting depth of 1. The current element starts
right after the opening bracket (or right after the previous top-level comma).

1. **Elements are separated by top-level commas.** A `,` at depth 1 ends the
   current element and starts a new one.
2. **Nesting.** Any of `[`, `(`, `{` increases the depth; any of `]`, `)`, `}`
   decreases it (bracket kinds are not matched against each other). Commas and
   colons at depth > 1 belong to the element text.
3. **End.** When the depth drops to 0, the current element is ended, and the
   function returns `sels` (all elements, in order), `out = ` everything after
   that closing bracket, and `ok = true`.
4. **Escapes and strings.** A `\` causes the next character to be skipped (it
   is kept in the element text but has no structural meaning, so `\,` `\:` and
   `\]` are literal). A `"` starts a quoted string that runs to the next `"`
   not escaped by `\` (a `\` inside the string skips the following character);
   brackets, commas and colons inside the string have no effect. The quotes
   stay part of the text.
5. **Names.** Within an element, the **first** `:` at depth 1 (outside strings,
   not escaped) separates the name from the path: `name` = text between the
   element start and that colon, `path` = text after the colon up to the end of
   the element. Further colons in the element are part of `path`. If there is
   no such colon, `name` is `""` and `path` is the whole element text. Names
   are taken verbatim (a quoted name keeps its quotes, e.g. `"abc"`).
6. **Modifiers disable names.** Once an `@` is seen whose preceding character
   is `.` or `|` (at any depth, outside strings), no further colon in the rest of
   the input (including all later elements) is treated as a name separator. An
   `@` preceded by any other character (e.g. `{@x:y}`) has no such effect.
7. **Empty elements are kept.** `[]` and `{}` yield one element with empty name
   and path; `{a,}` yields `a` and an empty element.
8. **Failure.** If the input ends before the depth returns to 0, `ok` is false
   and `out` is `""`. (The contents of `sels` in that case are not relied upon.)
9. Both `[` and `{` inputs follow exactly the same rules (names are recognised
   in both). The function does not modify its input and is safe for concurrent
   use. Element texts are substrings of the input (no unescaping, no trimming).

## 3. Input specification

- `path`: a Go string of length >= 1 whose first byte is `[` or `{` (a GJSON
  multipath, optionally followed by more path text such as `|@ugly` or
  `.@pretty`).

## 4. Output specification

- `sels`: the elements in input order, each a `subSelector{name, path}`.
- `out`: the remainder after the closing bracket (may be empty).
- `ok`: whether the closing bracket was found.

## 5. Edge cases and constraints

Each line shows the input (Go raw string), then `ok`, `out`, and the elements as
`{name path}` pairs (Go-quoted).

```
`[]`                       -> true ""  {"" ""}
`{}`                       -> true ""  {"" ""}
`[a]`                      -> true ""  {"" "a"}
`{a,b}`                    -> true ""  {"" "a"} {"" "b"}
`[0.first,1.extra.0]`      -> true ""  {"" "0.first"} {"" "1.extra.0"}
`{age,first|@case:upper}|@ugly`
                           -> true "|@ugly"  {"" "age"} {"" "first|@case:upper"}
`{friends.#.{age,first:first|@case:upper}|0.first}`
                           -> true ""  {"" "friends.#.{age,first:first|@case:upper}|0.first"}
`{abc:info.friends.0.first,info.friends.1.last,"abc":info.friends.1.kind,{123:x.cust2},[f.#[d.city="Phoenix"]#|#]}.@pretty.@ugly`
                           -> true ".@pretty.@ugly"  {"abc" "info.friends.0.first"} {"" "info.friends.1.last"}
                              {"\"abc\"" "info.friends.1.kind"} {"" "{123:x.cust2}"} {"" "[f.#[d.city=\"Phoenix\"]#|#]"}
`[a:b]`                    -> true ""  {"a" "b"}
`{a:b:c}`                  -> true ""  {"a" "b:c"}
`{:a}`                     -> true ""  {"" "a"}
`{a:}`                     -> true ""  {"a" ""}
`{a,}`                     -> true ""  {"" "a"} {"" ""}
`{,}`                      -> true ""  {"" ""} {"" ""}
`{a.@x,b:c}`               -> true ""  {"" "a.@x"} {"" "b:c"}      (modifier seen: no more names)
`{a|@m:1,b:c}`             -> true ""  {"" "a|@m:1"} {"" "b:c"}
`{@x:y,z:w}`               -> true ""  {"@x" "y"} {"z" "w"}
`{a\,b,c}`                 -> true ""  {"" "a\\,b"} {"" "c"}
`{"x,y":z}`                -> true ""  {"\"x,y\"" "z"}
`{"q\"}":r}rest`           -> true "rest"  {"\"q\\\"}\"" "r"}
`{a(b,c),d}`               -> true ""  {"" "a(b,c)"} {"" "d"}
`{a.#(b=="x,y")#,c}`       -> true ""  {"" "a.#(b==\"x,y\")#"} {"" "c"}
`{a:[b,c],d:{e:f}}tail`    -> true "tail"  {"a" "[b,c]"} {"d" "{e:f}"}
`[a]]]`                    -> true "]]"  {"" "a"}
`[x)`                      -> true ""  {"" "x"}
`{a`                       -> false ""
`[a,[b,c]`                 -> false ""
```

- Must run in time linear in the length of `path`.
