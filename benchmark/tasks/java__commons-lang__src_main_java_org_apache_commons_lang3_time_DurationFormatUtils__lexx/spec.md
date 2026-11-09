# Functional specification

## 1. Component overview

`DurationFormatUtils.lexx(format)` splits a duration format pattern (such as `"HH:mm:ss.SSS"` or `"'P'yyyy'Y'M'M'd'DT'H'H'm'M's.SSS'S'"`) into an array of `Token`s: runs of pattern letters and literal text.

## 2. Functional requirements

A `Token` has a value and a count: `new Token(Object value)` has count `1`, `Token(value, count)`, `getValue()`, `getCount()`, `increment()` (count + 1). The value of a pattern-letter token is one of the shared constants `y`, `M`, `d`, `H`, `m`, `s`, `S` (static `Object` constants of `DurationFormatUtils`, compared by identity); the value of a literal token is a `StringBuilder` holding the literal text (count 1).

Scan `format` from left to right, keeping three pieces of state: whether we are inside a quoted literal, the *current literal buffer* (a `StringBuilder` which is also the value of the last literal token in the list, or none), and the *previous letter token* (the most recently created letter token, or none). For each character `ch`:

1. If inside a quoted literal and `ch` is not `'`: append `ch` to the current literal text (no letter is interpreted) and continue.
2. If `ch` is `'`:
   - if inside a quoted literal: the literal ends (there is no current literal buffer afterwards);
   - otherwise: a new, empty literal token is appended to the list and becomes the current literal buffer, and we are now inside a quoted literal. (So `''` produces an empty literal token, and `'a''b'` produces two literal tokens `a` and `b`; there is no quote escaping.)
3. If `ch` is one of the pattern letters `y`, `M`, `d`, `H`, `m`, `s`, `S` (outside a quoted literal): if the previous letter token exists and has the same value, increment its count (even if other tokens, such as literals, were added after it; the count of the earlier token is increased and nothing is appended). Otherwise append a new letter token with count 1, which becomes the previous letter token. In both cases there is no current literal buffer afterwards.
4. Any other character outside a quoted literal: append it to the current literal buffer; if there is none, first append a new literal token to the list and make it the current buffer.

At the end, if still inside a quoted literal, throw `IllegalArgumentException` with the message `Unmatched quote in format: <format>`. Otherwise return the tokens in the order they were appended to the list, as a `Token[]`.

## 3. Input specification

`format`: a non-null `String` (possibly empty).

## 4. Output specification

A `Token[]`. Examples (`L"..."` is a literal token, `y*4` a letter token with count 4):
- `"yMdHmsS"` -> `y*1, M*1, d*1, H*1, m*1, s*1, S*1`
- `"HH:mm:ss.SSS"` -> `H*2, L":", m*2, L":", s*2, L".", S*3`
- `"'P'yyyy'Y'M'M'd'DT'H'H'm'M's.SSS'S'"` -> `L"P", y*4, L"Y", M*1, L"M", d*1, L"DT", H*1, L"H", m*1, L"M", s*1, L".", S*3, L"S"`
- `"d 'days'"` -> `d*1, L" ", L"days"`
- `"''"` -> `L""`; `"a''b"` -> `L"a", L"", L"b"`
- `"yy'x'y"` -> `y*3, L"x"`
- `""` -> empty array
- `"'abc"` -> `IllegalArgumentException`

## 5. Edge cases and constraints

- Linear time in the length of `format`.
- Characters that are neither quotes nor pattern letters (including `Y`, `D`, `T`, spaces and punctuation) are literal text.
- Pure function; thread-safe.
