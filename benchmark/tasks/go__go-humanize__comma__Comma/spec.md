# Functional specification: `func Comma(v int64) string`

## 1. Component overview

`Comma` is part of the `humanize` package (`github.com/dustin/go-humanize`),
which turns machine values into human-friendly text. `Comma` renders a signed
64-bit integer in decimal, with a comma separating each group of three digits
(the "thousands separator" style used in English). Other functions use it to
format counts, for example `english.Plural(1234567, "object", "")` gives
`"1,234,567 objects"`.

## 2. Functional requirements

1. Return the base-10 representation of `v`, with no leading zeros, a comma
   `,` between every group of three digits counted from the right, and a
   leading `-` for negative values.
2. Values with an absolute value below 1000 have no comma at all:
   `0 -> "0"`, `10 -> "10"`, `100 -> "100"`, `-10 -> "-10"`, `-100 -> "-100"`.
3. Every group after the first (leftmost) group has exactly three digits, so
   internal zeros are kept: `10001000 -> "10,001,000"`,
   `10010000 -> "10,010,000"`, `10100000 -> "10,100,000"`.
   The leftmost group has 1 to 3 digits.
4. Negative numbers are formatted like their absolute value, prefixed by `-`:
   `-123456789 -> "-123,456,789"`, `-1000 -> "-1,000"`.
5. The function is pure: no side effects, and the same input always gives the
   same output. It is safe for concurrent use.

More examples:

| `v` | result |
|---|---|
| `1000` | `"1,000"` |
| `10000` | `"10,000"` |
| `100000` | `"100,000"` |
| `10000000` | `"10,000,000"` |
| `123456789` | `"123,456,789"` |
| `9223372000000000000` | `"9,223,372,000,000,000,000"` |
| `-9223372000000000000` | `"-9,223,372,000,000,000,000"` |

## 3. Input specification

- `v`: any `int64`, from `math.MinInt64` (-9223372036854775808) to
  `math.MaxInt64` (9223372036854775807), inclusive.

## 4. Output specification

- A `string` made only of ASCII digits, commas, and possibly one leading `-`.
- No spaces, no `+` sign, no decimal point.
- Zero is `"0"`. There is never a `"-0"`.

## 5. Edge cases and constraints

- `math.MaxInt64` must give `"9,223,372,036,854,775,807"`.
- `math.MinInt64` must give `"-9,223,372,036,854,775,808"`. Its absolute value
  can't be represented as an `int64`, so the result must still be correct
  even though negating the value would overflow.
- The function never panics and never returns an error, for any `int64`.
