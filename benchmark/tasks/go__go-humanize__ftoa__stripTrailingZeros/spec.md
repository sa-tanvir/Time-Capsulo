# Functional specification: `func stripTrailingZeros(s string) string`

## 1. Component overview

`stripTrailingZeros` is an unexported helper of the `humanize` package
(`github.com/dustin/go-humanize`), in `ftoa.go`. The package formats floats
with a fixed number of decimals (for example `strconv.FormatFloat(x, 'f', 6, 64)`
gives `"2.200000"`) and then calls this helper to remove the redundant zeros
at the end of the fractional part. `Ftoa`, `FtoaWithDigits`, `SI` and
`SIWithDigits` all depend on it: `Ftoa(2.2)` is `"2.2"`, `Ftoa(200)` is `"200"`,
`SI(2.2e-10, "F")` is `"220 pF"`.

## 2. Functional requirements

1. Remove every `'0'` character at the end of the fractional part of `s`
   (the part after the decimal point).
2. If, after that, the decimal point is the last character, remove the
   decimal point too. In that case the result is just the integer part.
3. Digits of the integer part (before the `.`) are never removed, even if they
   are zeros: `"200.000000"` gives `"200"`, `"100.0"` gives `"100"`.
4. Non-zero fractional digits are kept, including zeros that are followed by a
   non-zero digit: `"2.020000"` gives `"2.02"`, `"200.020000"` gives `"200.02"`.
5. The result is always a prefix of `s` (the function only shortens the
   string; it never adds or changes characters).
6. The function is pure and safe for concurrent use.

Examples:

| `s` | result |
|---|---|
| `"2.000000"` | `"2"` |
| `"2.200000"` | `"2.2"` |
| `"2.020000"` | `"2.02"` |
| `"200.000000"` | `"200"` |
| `"200.020000"` | `"200.02"` |
| `"2.234500"` | `"2.2345"` |
| `"0.000000"` | `"0"` |
| `"-0.000000"` | `"-0"` |
| `"-12.500"` | `"-12.5"` |
| `"7."` | `"7"` |
| `"1.23"` | `"1.23"` |

## 3. Input specification

- `s`: a decimal number in fixed-point notation, as produced by
  `strconv.FormatFloat(x, 'f', prec, 64)` with `prec >= 0` or a truncation of
  such a string at some fractional digit. Concretely: an optional leading
  `-`, one or more ASCII digits, a single `.`, then zero or more ASCII digits.
- The fractional part may be long (hundreds or thousands of digits) and may
  end in a long run of zeros.

## 4. Output specification

- A `string` that is a prefix of `s`, as described above. It never ends with
  `.` and, when it contains a `.`, never ends with `0`.

## 5. Edge cases and constraints

- A fractional part made only of zeros (or empty) yields the integer part
  alone, with its sign: `"0.000000"` gives `"0"`, `"-0.000000"` gives `"-0"`,
  `"5."` gives `"5"`.
- A fraction with no trailing zeros is returned unchanged: `"3.14159"`.
- Only zeros directly at the end are affected; `"10.010"` gives `"10.01"`.
- The function never panics for inputs in the domain above.
