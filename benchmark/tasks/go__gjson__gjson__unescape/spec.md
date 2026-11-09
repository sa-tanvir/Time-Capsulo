# Functional specification: `func unescape(json string) string`

## 1. Component overview

`unescape` is an internal helper of the `gjson` package (`github.com/tidwall/gjson`),
which extracts values from JSON text. When a JSON string literal contains
backslash escape sequences, the library passes the literal's body (the text
between the opening and the closing quote, quotes excluded) to `unescape` to get
the decoded Go string that ends up in `Result.Str` (and in object keys). It must
be lenient: malformed input never causes a panic; decoding simply stops.

## 2. Functional requirements

The input is processed left to right, appending to the output:

1. **Ordinary bytes.** Every byte `>= 0x20` (space) that is not a backslash is
   copied unchanged. This includes `"`, `/`, DEL (0x7F) and every byte of
   multi-byte UTF-8 sequences (raw UTF-8 passes through untouched, valid or
   not).
2. **Raw control bytes stop decoding.** On a byte `< 0x20` (e.g. a literal
   newline, tab or NUL), return the output produced so far; the rest is
   dropped.
3. **Simple escapes.** A backslash followed by one of these characters appends:
   `\\` -> `\`, `\/` -> `/`, `\"` -> `"`, `\b` -> 0x08, `\f` -> 0x0C,
   `\n` -> 0x0A, `\r` -> 0x0D, `\t` -> 0x09.
4. **Unknown or truncated escapes stop decoding.** A backslash that is the last
   byte, or that is followed by any other character (e.g. `\x`, `\q`, `\'`),
   ends decoding: return the output so far (the backslash and everything after
   it are dropped).
5. **`\u` escapes.** `\u` must be followed by at least 4 more bytes; if fewer
   than 4 bytes remain after the `u`, decoding stops (return the output so
   far). Otherwise those 4 bytes are read as a hexadecimal code unit
   (upper- or lower-case digits). If they are not 4 valid hex digits, the code
   unit is 0 (U+0000). Then:
   - If the code unit is a UTF-16 surrogate (0xD800–0xDFFF) **and** the next
     6 bytes exist and start with `\u`, those 6 bytes are consumed as a second
     code unit (again 0 if not valid hex), and the pair is combined as a UTF-16
     surrogate pair. If the two do not form a valid high+low pair (e.g. the
     first is a low surrogate, or the second is not a low surrogate), the
     result is a single U+FFFD and **both** escapes are still consumed.
   - A surrogate that is not followed by at least 6 bytes starting with `\u`
     becomes U+FFFD on its own; nothing after it is consumed and the following
     text is processed normally (e.g. `\ud83dabc` and `\ud83dA`).
   - The resulting code point is appended encoded as UTF-8 (U+0000 is a
     single 0x00 byte).
6. Returns the output as a Go `string`. Pure, no side effects, safe for
   concurrent use.

## 3. Input specification

- `json`: any Go string (possibly empty, arbitrary bytes). Usually the body of a
  JSON string literal, without the surrounding quotes.

## 4. Output specification

- The decoded `string`. Its length never exceeds what the decoded escapes
  produce; for an input without backslashes or control bytes the output equals
  the input.

## 5. Edge cases and constraints

Inputs are shown as raw text (`<NUL>` is a 0x00 byte, `<LF>` a 0x0A byte).

| input | output |
|---|---|
| (empty) | (empty) |
| `plain text` | `plain text` |
| `\\<NUL>` | `\` (the NUL stops decoding) |
| `\/\b\f` | `/`, 0x08, 0x0C |
| `\"quoted\"` | `"quoted"` |
| `tab\there` | `tab`, 0x09, `here` |
| `été` | `été` |
| `中中` | `中中` |
| `😀` | `😀` (U+1F600) |
| `𝄞` | `𝄞` (U+1D11E) |
| `\ud83d` | U+FFFD |
| `\ud83dabc` | U+FFFD then `abc` |
| `\ude00\ud83d` | U+FFFD (one character; both escapes consumed) |
| `\ud83dA` | U+FFFD then `A` (fewer than 6 bytes follow, so nothing extra is consumed) |
| `\ud83d\uzzzz` | U+FFFD |
| `\ud83d\u12` | U+FFFD (then `\u12` is truncated -> stop) |
| `end\ud83d\` | `end` then U+FFFD |
| `\u0000x` | 0x00 then `x` |
| `\uzzzzx` | 0x00 then `x` (invalid hex reads as 0) |
| `\u12`, `\u123` | (empty) |
| `ab\` | `ab` |
| `ab\x` | `ab` |
| `a<LF>b` | `a` |
| `a`, 0x7F, `b` | unchanged (0x7F is not a control byte here) |
| `\\\\` (4 backslashes) | `\\` |

- Must run in time linear in the input length.
