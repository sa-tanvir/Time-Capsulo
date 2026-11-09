# Functional specification: `unquote_unreserved(uri)`

## 1. Component overview

A helper in `requests.utils` used when re-quoting URLs (`requote_uri`). It
decodes percent-escapes that stand for **unreserved** URI characters
(letters, digits, `-`, `.`, `_`, `~`) and leaves every other `%` sequence
(reserved characters, illegal bytes, non-ASCII bytes, malformed escapes)
exactly as it is, so that re-quoting the URI later neither double-encodes
nor changes its meaning.

## 2. Functional requirements

1. Scan the string for `%` characters from left to right. Text that is not
   part of a percent-escape is copied unchanged.
2. For each `%`, look at the (up to) two characters that immediately follow
   it:
   - If there are fewer than two characters, or the two characters are not
     both alphanumeric (`str.isalnum()` on the pair), the `%` and everything
     after it are kept literally (`'%--'` stays `'%--'`, a trailing `'%'` or
     `'%4'` at the end of the string stays).
   - "Alphanumeric" and "valid hexadecimal number" have Python's meaning:
     the pair passes `str.isalnum()` (Unicode letters/digits included), and
     it is valid hex when `int(pair, 16)` succeeds. `int` accepts any Unicode
     decimal digit (category Nd, e.g. Arabic-Indic `'٤١'` or full-width
     `'４１'` both read as 0x41, so they decode to `'A'`), but only ASCII
     `a`-`f`/`A`-`F` as letter digits; other alphanumerics such as `'é'`,
     `'²'` or `'ß'` make the pair invalid.
   - If both are alphanumeric but do not form a valid hexadecimal number
     (e.g. `'%zz'`, `'%G1'`, `'%é1'`), raise `InvalidURL` with the message
     `"Invalid percent-escape sequence: '<two chars>'"` (e.g.
     `Invalid percent-escape sequence: 'zz'`).
   - If they form a hexadecimal number (case-insensitive) whose character
     (code point = the number) is in `UNRESERVED_SET`, replace the three
     characters `%XX` by that single character (`'%41'` → `'A'`,
     `'%7e'`/`'%7E'` → `'~'`, `'%2D'` → `'-'`, `'%30'` → `'0'`).
   - Otherwise (reserved or non-ASCII byte: `'%2F'`, `'%20'`, `'%25'`,
     `'%C3'`, ...) keep `%XX` unchanged, preserving the original case of the
     hex digits.
3. Each `%` is considered only once and characters produced by decoding are
   never re-examined: `'%2541'` stays `'%2541'` (the `%25` is reserved and
   kept; `41` is plain text), and `'%%41'` gives `'%A'` (the first `%` is
   followed by `%4`, which is not alphanumeric, so it is kept; the second
   `%41` decodes).
4. Return the resulting string.

## 3. Input specification

- `uri`: `str` (any text; typically a URL that may contain percent-escapes).

## 4. Output specification

A `str`.

| uri | result |
|---|---|
| `'http://example.com/?a=%--'` | `'http://example.com/?a=%--'` |
| `'http://example.com/?a=%300'` | `'http://example.com/?a=00'` |
| `'http://example.com/fiz?buz=%25ppicture'` | unchanged |
| `'/path%7Efoo%2Fbar'` | `'/path~foo%2Fbar'` |
| `'%61%62%63%2e%5F'` | `'abc._'` |
| `'stra%C3%9Fe'` | unchanged |
| `'no escapes'` | unchanged |
| `'buz=%ppicture'` | raises `InvalidURL("Invalid percent-escape sequence: 'pp'")` |

## 5. Edge cases and constraints

- Empty string → `''`.
- Pure function; no side effects.
- `InvalidURL` comes from `requests.exceptions` (imported in this module).
  `requote_uri` relies on this exception to detect stray `%` signs, so it
  must be raised (not silently ignored) for alphanumeric non-hex pairs.
