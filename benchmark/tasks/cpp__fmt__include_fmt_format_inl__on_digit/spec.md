# Functional specification: `fixed_handler::on_digit(digit, divisor, remainder, error, exp, integral)`

## 1. Component overview

`fixed_handler` receives the decimal digits of a floating-point number one by one from the Grisu digit generator, when the caller asked for a fixed number of digits (`precision`). `on_digit` is called once per generated digit. It appends the digit to the output buffer and decides whether the generator should keep going, whether the requested precision has been reached (in which case the last digit is rounded using the remaining fraction), or whether the fast algorithm cannot decide and the caller has to use a slower fallback.

## 2. Functional requirements

State read and written: `buf` (digit characters), `size` (digits stored), `precision` (digits wanted). Arguments: `digit` (ASCII `'0'..'9'`), `divisor` (the weight of one unit of the digit just produced, in the scaled arithmetic of the generator), `remainder` (what is left of the number below the digit just produced, `remainder < divisor`), `error` (the uncertainty of `remainder`, an absolute value in the same scale), the unused `int` argument, and `integral` (true while the digit comes from the integral part of the scaled number).

1. Store `digit` at `buf[size]` and increase `size` by one.
2. If the new `size` is still **less than** `precision`, return `digits::more` (nothing else happens).
3. Otherwise the requested number of digits has been reached (or exceeded) and rounding is decided:
   1. If `integral` is false and the error is too large to decide anything, that is `error >= divisor` or `error >= divisor - error`, return `digits::error` (the digit stays stored).  When `integral` is true no such check is made (there `error == 1` and `divisor > 2`).
   2. Determine the rounding direction with `get_round_direction(divisor, remainder, error)`.
   3. If the direction is not `up`: return `digits::done` when it is `down`, and `digits::error` when it is `unknown`.
   4. If the direction is `up`: round the digit string up. Increase the last stored digit by one; when a digit becomes greater than `'9'` it turns into `'0'` and one is added to the digit before it, repeatedly (a carry). If the carry goes beyond the first digit, the first digit becomes `'1'` and one extra `'0'` is appended (`size` grows by one), e.g. `999` becomes `1000`. Then return `digits::done`.
4. The function never changes `precision`, `exp10`, `fixed` or `buf` characters other than as described.

Examples (digits already stored before the call -> after, result):
- stored `12`, `precision` 5, digit `3` -> `123`, `more`.
- stored `12`, `precision` 3, digit `3`, remainder well below half of the divisor, small error -> `123`, `done`.
- stored `12`, `precision` 3, digit `3`, remainder well above half -> `124`, `done`.
- stored `99`, `precision` 3, digit `9`, round up -> `1000` (size 4), `done`.
- stored `19`, `precision` 3, digit `9`, round up -> `200`, `done`.
- remainder close to half of the divisor relative to the error (neither clearly down nor clearly up) -> `error`.

## 3. Input specification

- `digit`: one of `'0'`..`'9'`. `divisor > 0`, `remainder < divisor`. If `integral` is false then `error` may be anything below `divisor`; if it is true then `error == 1` and `divisor > 2`. `buf` has room for `size + 2` characters. `size >= 0`; `precision` may be smaller than or equal to the size after storing (e.g. 0).

## 4. Output specification

Returns a `digits::result` (`more`, `done`, `error`). Mutates `buf` and `size` as described.

## 5. Edge cases and constraints

- With `precision <= size + 1` before the call, rounding is always attempted.
- Rounding only touches the digits already stored; the carry never reads before `buf[0]`.
- A result of `error` does not undo the stored digit: `size` stays increased by one.
- The function must be allocation-free and cheap: it is called for every generated digit.
