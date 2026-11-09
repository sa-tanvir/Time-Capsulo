# Functional specification: `func Commaf(v float64) string`

## 1. Component overview

`Commaf` is part of the `humanize` package (`github.com/dustin/go-humanize`),
which turns machine values into human-friendly text. It renders a `float64`
in plain decimal notation (never scientific notation) and inserts a comma
between every group of three digits of the **integer part** (English
thousands separators). The fractional part, if any, is kept exactly and is
not grouped. `CommafWithDigits(f, decimals)` in the same file builds on it by
cutting the result to a number of decimal places.

## 2. Functional requirements

1. **Digits.** The digits written are those of the shortest decimal string
   that converts back to exactly the same `float64` value, written in
   fixed-point form without an exponent. This is exactly the digit string of
   `strconv.FormatFloat(x, 'f', -1, 64)`, where `x` is `-v` when `v < 0` and
   `v` itself otherwise (negative zero is not `< 0`, so it is formatted as
   is, see rule 4).
   Consequently:
   - integral values have no decimal point: `100` gives `"100"`, not
     `"100.0"`;
   - very large values are padded with zeros instead of an exponent:
     `1e21` gives `"1,000,000,000,000,000,000,000"`;
   - very small values are written out in full: `1e-7` gives `"0.0000001"`.
2. **Grouping.** The integer part (everything before the decimal point) is
   split into groups of three digits counted from the right, separated by
   `,`. The leftmost group has 1 to 3 digits. Integer parts of 1 to 3
   digits contain no comma. Internal zeros are kept: `10001000` gives
   `"10,001,000"`.
3. **Fraction.** If the value has a fractional part, it follows the
   grouped integer part as `.` plus its digits, unchanged and without any
   separators: `834142.32` gives `"834,142.32"`, `100000.25` gives
   `"100,000.25"`.
4. **Sign.** A value strictly less than zero is written as `-` followed by
   the formatting of `-v`: `-123456789` gives `"-123,456,789"`, `-100.11`
   gives `"-100.11"`. Negative zero compares equal to zero, so it is not
   "below zero"; it is formatted directly, and since its shortest decimal
   form is `"-0"`, the result is `"-0"`.
5. The function is pure and safe for concurrent use.

Examples:

| `v` | result |
|---|---|
| `0` | `"0"` |
| `10.11` | `"10.11"` |
| `100` | `"100"` |
| `1000` | `"1,000"` |
| `100000` | `"100,000"` |
| `834142.32` | `"834,142.32"` |
| `10010000` | `"10,010,000"` |
| `123456789` | `"123,456,789"` |
| `999.5` | `"999.5"` |
| `-10` | `"-10"` |
| `-1000` | `"-1,000"` |
| `-10100000` | `"-10,100,000"` |
| `math.MaxFloat64` | see section 5 |
| `math.SmallestNonzeroFloat64` | `"0."` followed by 323 zeros and a final `5` |

## 3. Input specification

- `v`: any finite `float64` (negative, zero, positive; from
  `math.SmallestNonzeroFloat64` up to `math.MaxFloat64` in magnitude).
- NaN and infinities are outside the contract.

## 4. Output specification

- A `string` consisting of an optional leading `-`, the grouped integer
  part, and optionally `.` followed by the fractional digits.
- No exponent, no `+` sign, no trailing zeros in the fractional part (the
  shortest representation never has them), and no decimal point for
  integral values.

## 5. Edge cases and constraints

- `0` gives `"0"`. Negative zero (`math.Copysign(0, -1)`) gives `"-0"`
  (rule 4: it is not below zero, but its shortest decimal form `"-0"`
  carries the sign; no comma is inserted).
- Values whose magnitude is below 1 have integer part `"0"`:
  `0.5` gives `"0.5"`, `-0.25` gives `"-0.25"`.
- Integer parts whose digit count is a multiple of three start with a full
  group: `123456.5` gives `"123,456.5"`.
- `math.MaxFloat64` must give
  `"179,769,313,486,231,570"` followed by 97 more groups `",000"`
  (309 integer digits in total).
- The function never panics for finite inputs.
