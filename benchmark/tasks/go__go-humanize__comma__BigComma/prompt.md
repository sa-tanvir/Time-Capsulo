You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func BigComma(b *big.Int) string`

## 1. Component overview

`BigComma` is part of the `humanize` package (`github.com/dustin/go-humanize`),
which turns machine values into human-friendly text. It is the arbitrary-
precision counterpart of `Comma`: it renders a `*big.Int` (from `math/big`)
in base 10 with a comma between every group of three digits (English
thousands separators). Integers of any size must be supported, including
values with hundreds or thousands of digits.

## 2. Functional requirements

1. Return the base-10 representation of the value of `b`, with no leading
   zeros, a comma `,` between every group of three digits counted from the
   right, and a leading `-` for negative values.
2. Values whose absolute value is below 1000 contain no comma:
   `0 -> "0"`, `10 -> "10"`, `100 -> "100"`, `-10 -> "-10"`, `-100 -> "-100"`.
3. Every group after the leftmost one has exactly three digits, so internal
   zeros are kept: `10001000 -> "10,001,000"`, `10010000 -> "10,010,000"`,
   `10100000 -> "10,100,000"`. The leftmost group has 1 to 3 digits.
4. Negative values are formatted like their absolute value, prefixed by `-`:
   `-123456789 -> "-123,456,789"`, `-1000 -> "-1,000"`.
5. **Argument state.** The function is allowed to modify the `big.Int` that
   `b` points to while computing the result; after the call, the value held
   by `*b` is unspecified. Callers that still need the value must pass a
   copy. (Leaving `*b` unchanged is also acceptable.) The returned string
   must describe the value `b` had when the call started.
6. Calls on distinct `big.Int` values are independent; concurrent calls on
   the same `*big.Int` are not supported.

Examples:

| value of `b` | result |
|---|---|
| `1000` | `"1,000"` |
| `10000` | `"10,000"` |
| `100000` | `"100,000"` |
| `10000000` | `"10,000,000"` |
| `123456789` | `"123,456,789"` |
| `9223372000000000000` | `"9,223,372,000,000,000,000"` |
| `-9223372000000000000` | `"-9,223,372,000,000,000,000"` |
| `84889279597249724975972597249849757294578485` | `"84,889,279,597,249,724,975,972,597,249,849,757,294,578,485"` |
| `-84889279597249724975972597249849757294578485` | `"-84,889,279,597,249,724,975,972,597,249,849,757,294,578,485"` |

## 3. Input specification

- `b`: a non-nil `*big.Int` holding any integer, positive, zero or negative,
  of any magnitude (tested up to thousands of decimal digits).

## 4. Output specification

- A `string` of ASCII digits and commas, with possibly one leading `-`.
- No spaces, no `+`, no leading zeros (except the single digit `"0"` for
  zero). Zero is `"0"`, never `"-0"`.

## 5. Edge cases and constraints

- Values beyond the `int64` range must be handled exactly
  (e.g. `2^64 = 18446744073709551616` gives `"18,446,744,073,709,551,616"`).
- Exact multiples of large powers of 1000 keep all zero groups:
  `10^12` gives `"1,000,000,000,000"`.
- The function never panics and never returns an error for a non-nil `b`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `comma.go`

## Imports / includes available in this file

```
import "bytes"
import "math"
import "math/big"
import "strconv"
import "strings"
```

## Other functions defined in the same file (signatures only; you may call them)

```
Comma v int64
Commaf v float64
CommafWithDigits f float64 , decimals int
```

=== STUB ===
```go
func BigComma(b *big.Int) string {
    // TODO: implement according to the specification
}
```
