# Functional specification: `func oomm(n, b *big.Int, maxmag int) (float64, int)`

## 1. Component overview

`oomm` ("order of magnitude, with a maximum") is an unexported helper of the
`humanize` package (`github.com/dustin/go-humanize`), in `big.go`. It works on
arbitrary-precision integers (`math/big`). Given a non-negative number `n` and
a base `b`, it finds how many times `n` can be scaled down by `b` (the
magnitude, optionally capped at `maxmag`) and returns the scaled-down value
as a `float64` together with that magnitude. `BigBytes` and `BigIBytes` use it
with base 1000 or 1024 and a cap equal to the number of unit names, e.g. to
turn `15347691069326346944512` bytes into `"15 ZB"` / `"13 ZiB"`, and
`16093220510709943573688614912` into `"16093 YB"` (the cap stops the scaling
at the largest unit).

## 2. Functional requirements

Let `N` be the value of `n` at the start of the call and `B` the value of `b`.

1. **Magnitude.** The returned `mag` is the number of whole scaling steps
   performed, where one step replaces the current value `x` by `floor(x / B)`.
   Steps are performed while the current value is `>= B`.
   - If `maxmag >= 1`, scaling stops as soon as `mag` reaches `maxmag`, even
     if the current value is still `>= B`.
   - If `maxmag <= 0` there is no cap: scaling continues until the current
     value is below `B`. (Note: `maxmag == 0` behaves like "no cap", not
     like "zero steps".)
   - If `N < B`, no step is performed and `mag` is `0`.
2. **Value.** Let `q` be the value after the last step, i.e. `floor(N / B^mag)`,
   and let `r` be the remainder of the last step, i.e.
   `floor(N / B^(mag-1)) mod B` (and `r = 0` when `mag == 0`). The returned
   float is exactly the `float64` expression
   `float64(q) + float64(r)/float64(B)`, computed in that order with ordinary
   `float64` arithmetic. Only the remainder of the **last** step contributes
   to the fractional part; lower-order digits are discarded.
3. **Argument state.** `n` may be overwritten by the function (callers pass a
   scratch copy); its value after the call is unspecified. `b` must not be
   modified.
4. The function has no other side effects.

Examples (`(value, mag)`):

| `N` | `B` | `maxmag` | result |
|---|---|---|---|
| `5` | `10` | `-1` | `(5, 0)` |
| `999` | `1000` | `8` | `(999, 0)` |
| `1500` | `1000` | `8` | `(1.5, 1)` |
| `12345` | `10` | `-1` | `(1.2, 4)` |
| `12345` | `10` | `0` | `(1.2, 4)` |
| `12345` | `10` | `2` | `(123.4, 2)` |
| `123456789` | `1000` | `1` | `(123456.789, 1)` |
| `5242880` | `1024` | `1` | `(5120, 1)` |
| `5242880` | `1024` | `8` | `(5, 2)` |
| `1024` | `1000` | `8` | `(1.024, 1)` |

## 3. Input specification

- `n`: non-nil `*big.Int`, value `>= 0`, of any size (up to thousands of
  decimal digits).
- `b`: non-nil `*big.Int`, value `>= 2` and small enough to fit in an
  `int64`.
- `maxmag`: any `int`; values `<= 0` mean "no cap".
- The inputs are always such that the final `q` fits in an `int64`
  (automatically true without a cap, since then `q < B`).

## 4. Output specification

- First result: `float64(q) + float64(r)/float64(B)` as defined above.
- Second result: `mag`, the number of steps performed (`0 <= mag`, and
  `mag <= maxmag` when `maxmag >= 1`).

## 5. Edge cases and constraints

- `N == 0` or any `N < B`: returns `(float64(N), 0)`.
- `N == B`: one step, `q = 1`, `r = 0`, returns `(1, 1)`.
- With a cap, `q` may be much larger than `B` (e.g. `(123456.789, 1)` above).
- The result must be identical bit-for-bit to the expression in rule 2;
  in particular, do not include lower-order digits in the fraction, and do
  not compute the value as `N / B^mag` in floating point.
- The function never panics for inputs in the contract.
