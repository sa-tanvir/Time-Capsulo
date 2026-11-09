# Functional specification: `file_helper::split_by_extension(fname)`

## 1. Component overview

A helper of spdlog's file sinks. It splits a file name or path into a *base* (the path without its extension) and an *extension* (including the leading dot), for example to insert a date or a rotation index before the extension. It is a pure string function.

## 2. Functional requirements

Let *last dot* be the position of the last `.` character in the whole string, and *last separator* the position of the last folder separator `/`.

The function returns a pair `(base, ext)` with `base + ext == fname` in every case.

1. If an extension is recognised, `ext` is the substring from the last dot to the end of the string (dot included) and `base` is everything before the last dot.
2. Otherwise `base` is the whole input and `ext` is the empty string.

The last dot does **not** start an extension (rule 2 applies) in any of these cases:
- there is no dot in the string;
- the last dot is the very first character of the string (a hidden file such as `.mylog`);
- the last dot is the very last character (`mylog.`, a trailing dot);
- there is a separator, and the last separator lies at or after the position immediately before the last dot. This covers a dot that belongs to a directory name (the last separator comes after the dot, as in `/aaa/bb.d/mylog`, `.././mylog.txt/xxx`) and a dot that directly follows a separator (a hidden file in a directory: `my_folder/.mylog`, `/abc/.hidden`).

Only the last dot is considered: `a.b.c` gives `("a.b", ".c")`. A dot that is not directly preceded by a separator and is not the first character is a valid extension start even when the base ends up looking odd (`..txt` gives `(".", ".txt")`, `a..b` gives `("a.", ".b")`).

## 3. Input specification

`fname`: any `std::string` (possibly empty, no embedded NUL), taken as a path using `/` as folder separator.

## 4. Output specification

A `std::tuple<std::string, std::string>` `(base, ext)` as described. No exceptions are thrown. The input is not modified.

## 5. Edge cases and constraints

| input | base | ext |
|---|---|---|
| `mylog.txt` | `mylog` | `.txt` |
| `.mylog.txt` | `.mylog` | `.txt` |
| `.mylog` | `.mylog` | (empty) |
| `/aaa/bb.d/mylog` | `/aaa/bb.d/mylog` | (empty) |
| `/aaa/bb.d/mylog.txt` | `/aaa/bb.d/mylog` | `.txt` |
| `aaa/bbb/ccc/mylog.` | `aaa/bbb/ccc/mylog.` | (empty) |
| `aaa/bbb/ccc/.mylog.txt` | `aaa/bbb/ccc/.mylog` | `.txt` |
| `/aaa/bbb/ccc/.mylog` | `/aaa/bbb/ccc/.mylog` | (empty) |
| `../mylog.txt` | `../mylog` | `.txt` |
| `.././mylog.txt/xxx` | `.././mylog.txt/xxx` | (empty) |
| `//mylog.txt` | `//mylog` | `.txt` |
| (empty string) | (empty) | (empty) |
| `.` | `.` | (empty) |
| `..txt` | `.` | `.txt` |

Paths may be long (thousands of characters); the function is called on every file rotation, so keep it cheap.
