# Functional specification: `encode(str, defaultEncoder, charset)` in `lib/utils.js`

## 1. Component overview

The default percent-encoder of the `qs` library (exported as `utils.encode`). It
is used by `qs.stringify` to encode every key and every value of the query string,
and it is the function handed to custom encoders as their `defaultEncoder`
argument. It follows RFC 3986 strictly in UTF-8 mode and mimics a legacy
browser-style encoding in ISO-8859-1 mode.

## 2. Functional requirements

1. **Empty input.** If `str.length === 0`, return `str` itself unchanged (the empty
   string gives `''`; an empty Buffer is returned as the same Buffer object).
2. **Conversion to text.** A Symbol is converted with `Symbol.prototype.toString`
   (giving e.g. `'Symbol(Symbol.iterator)'`); any other non-string (number,
   boolean, BigInt, Buffer, ...) is converted with `String(x)` (a Buffer becomes
   its UTF-8 text). Strings are used as is.
3. **`charset === 'iso-8859-1'`.** The result is exactly what the legacy global
   `escape()` produces for the text, except that every `%uXXXX` sequence it would
   produce is replaced by `%26%23` + the decimal value of `XXXX` + `%3B` (the
   URL-encoded HTML numeric entity `&#N;`). Concretely:
   - `A-Z a-z 0-9 @ * _ + - . /` are kept;
   - other code units below 256 become `%XX` with two upper-case hex digits
     (`'æ'` -> `%E6`, `' '` -> `%20`, `'~'` -> `%7E`);
   - each UTF-16 code unit of 256 or above becomes `%26%23<decimal>%3B`
     (`'☺'` -> `%26%239786%3B`; the two halves of a surrogate pair become two
     separate entities: `'𐐷'` -> `%26%2355297%3B%26%2356375%3B`).
4. **Any other charset (UTF-8, the default; also `undefined` or unknown values).**
   - The unreserved characters `A-Z a-z 0-9 - . _ ~` are kept;
   - every other character is replaced by the percent-encoding of its UTF-8 bytes,
     using upper-case hex, one `%XX` per byte: 1 byte below U+0080, 2 bytes below
     U+0800, 3 bytes for the rest of the BMP, 4 bytes for supplementary characters
     given as surrogate pairs.
   - A code unit in the surrogate range U+D800–U+DFFF is always treated as the
     first half of a pair together with the next code unit: the code point is
     `0x10000 + ((first & 0x3FF) << 10 | (next & 0x3FF))`, a missing next unit
     counting as 0 (so a lone `'\ud800'` gives `%F0%90%80%80`). Both units are
     consumed.
5. `defaultEncoder` is accepted for call-signature compatibility and is ignored.

## 3. Input specification

- `str`: usually a string; may also be a number, boolean, Symbol, BigInt or
  Buffer (anything with a `length` property or convertible by `String`). `null`
  and `undefined` are not valid.
- `defaultEncoder`: any value (ignored).
- `charset`: `'utf-8'`, `'iso-8859-1'`, or `undefined`.

## 4. Output specification

A string (or, for zero-length input, the input itself). Examples:

| input | charset | output |
|---|---|---|
| `'b'` / `'A_Z'` | utf-8 | `b` / `A_Z` |
| `'€'` | utf-8 | `%E2%82%AC` |
| `''` | utf-8 | `%EE%80%80` |
| `'א'` | utf-8 | `%D7%90` |
| `'𐐷'` | utf-8 | `%F0%90%90%B7` |
| `'b c'` | utf-8 | `b%20c` |
| `'a[b]'` | utf-8 | `a%5Bb%5D` |
| `'~q1!2"\'w$5&7/z8)?'` | utf-8 | `~q1%212%22%27w%245%267%2Fz8%29%3F` |
| `'@*_+-./~ !'` | utf-8 | `%40%2A_%2B-.%2F~%20%21` |
| `'@*_+-./~ !'` | iso-8859-1 | `@*_+-./%7E%20%21` |
| `'æ'` | utf-8 / iso-8859-1 | `%C3%A6` / `%E6` |
| `'✓'` | utf-8 / iso-8859-1 | `%E2%9C%93` / `%26%2310003%3B` |
| `12.5`, `true` | utf-8 | `12.5`, `true` |
| `Symbol.iterator` | utf-8 | `Symbol%28Symbol.iterator%29` |
| `Buffer.from('a b')` | utf-8 | `a%20b` |
| `''` | any | `''` |

## 5. Edge cases and constraints

- Hex digits are always upper case.
- Space is always `%20` (never `+`); turning `%20` into `+` is the job of the
  RFC1738 formatter, not of this function.
- Pure function: no mutation of the input, no global state.
- Must work when the global `Buffer` is absent.
- Must be fast on long strings (called for every key and value of a query string).
