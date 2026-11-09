# Functional specification: `RoundWeedCounted(buffer, length, rest, ten_kappa, unit, kappa)`

## 1. Component overview

Part of the Grisu3 fixed-count double-to-string conversion in the double-conversion library (precision mode: a fixed number of significant digits is requested). The digit generator has written `length` digits into `buffer`, and what is left over is `rest`, a fixed-point remainder with `rest < ten_kappa`, where `ten_kappa` is the value of one unit of the last written digit. The remainder is only known up to an error of `unit`. `RoundWeedCounted` decides whether the digits can be rounded safely (down, which needs no change, or up, which changes the digits), or whether the precision is too low to decide. It returns `true` when the digits in `buffer` are correct after the call and `false` when no safe decision is possible (the caller then uses a slower algorithm).

## 2. Functional requirements

All of `rest`, `ten_kappa`, `unit` are unsigned 64-bit integers in the same fixed-point unit and `rest < ten_kappa`. Apply these rules in order and stop at the first that applies:

1. If `unit >= ten_kappa`, return `false` (the error is as large as a whole last digit).
2. If `ten_kappa - unit <= unit`, return `false` (the error is at least half of a last digit, so the rounding direction is unknown).
3. If rounding down is safe, return `true` and leave the digits unchanged. Rounding down is safe when `rest + unit` is at most half of `ten_kappa`, which is written without overflow as `ten_kappa - rest > rest` and `ten_kappa - 2 * rest >= 2 * unit`.
4. If rounding up is safe, round the digits up and return `true`. Rounding up is safe when `rest - unit` is at least half of `ten_kappa`, which is written without underflow as `rest > unit` and `ten_kappa - (rest - unit) <= rest - unit`. Rounding up means: add one to the last digit; a digit that becomes `'9' + 1` (the character after `'9'`) is turned into `'0'` and one is added to the digit before it, and so on towards the front. If the first digit overflows in this way it becomes `'1'` (all other digits are then `'0'`) and `*kappa` is increased by one (the number of digits is not changed: `"99"` becomes `"10"` with `kappa + 1`).
5. Otherwise return `false` and leave everything unchanged.

`*kappa` is changed only in the case described in rule 4; `length` and all other arguments are never changed. The buffer is changed only by rule 4.

## 3. Input specification

- `buffer`: `Vector<char>` holding at least `length` ASCII digits, `length >= 1`.
- `length`: `int`.
- `rest`, `ten_kappa`, `unit`: `uint64_t`, with `rest < ten_kappa < 2^62`, `unit` any value (it can be larger than `ten_kappa`).
- `kappa`: non-null `int*` with the current decimal exponent of the last digit.

## 4. Output specification

`bool`; the digits may be incremented as in rule 4, and `*kappa` may be increased by one.

## 5. Edge cases and constraints

| buffer | rest | ten_kappa | unit | kappa before | result | buffer after | kappa after |
|---|---|---|---|---|---|---|---|
| `12345` | 3 | 10 | 1 | 0 | true | `12345` | 0 |
| `12345` | 4 | 10 | 1 | 0 | true | `12345` | 0 |
| `12345` | 5 | 10 | 1 | 0 | false | `12345` | 0 |
| `12345` | 7 | 10 | 1 | 0 | true | `12346` | 0 |
| `12999` | 9 | 10 | 1 | 0 | true | `13000` | 0 |
| `99999` | 9 | 10 | 1 | 0 | true | `10000` | 1 |
| `99999` | 9 | 10 | 1 | 5 | true | `10000` | 6 |
| `9` | 9 | 10 | 1 | 0 | true | `1` | 1 |
| `1` | 9 | 10 | 1 | 0 | true | `2` | 0 |
| `12345` | 6 | 10 | 2 | 0 | false | `12345` | 0 |
| `12345` | 9 | 10 | 4 | 0 | true | `12346` | 0 |
| `12345` | 9 | 100 | 4 | 0 | true | `12345` | 0 |
| `12345` | 4 | 10 | 5 | 0 | false | `12345` | 0 |
| `12345` | 0 | 10 | 0 | 0 | true | `12345` | 0 |

The checks are written so that no unsigned subtraction wraps around and no multiplication overflows for `rest < ten_kappa < 2^62`.
