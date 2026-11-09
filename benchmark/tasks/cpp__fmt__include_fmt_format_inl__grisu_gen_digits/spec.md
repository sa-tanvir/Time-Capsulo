# Functional specification: `grisu_gen_digits(value, error, exp, handler)`

## 1. Component overview

The digit-generation step of the Grisu floating-point printing algorithm used by fmt. Given a number that has been scaled by a power of ten into a convenient binary range, it produces its decimal digits one by one, most significant first, and feeds each digit, together with the information needed to round it, to a *handler* object. The handler decides when enough digits have been generated (and whether rounding succeeded). The function returns the handler's final decision.

## 2. Functional requirements

Input number: `value` is the fixed-point number `value.f / 2^(-value.e)`, with `value.e` in `[-60, -32]`. Write `S = -value.e` (the number of fractional bits) and `one = 2^S`. The **integral part** is `I = value.f >> S` (a non-zero value that fits in 32 bits), the **fractional part** is `Fr = value.f mod one` (an integer below `one`, i.e. the fraction scaled by `one`). `error` is the uncertainty of the number in units of `1/one`.

The function performs these steps in order, using the handler for decisions:

1. **Start.** Set `exp` to the number of decimal digits of `I`. Call `on_start` on the handler with four arguments: the weight of the leading digit (`10^(exp-1)` scaled by `one`, i.e. times `2^S`), one tenth of `value.f` (integer division), ten times `error`, and `exp` itself, passed by reference (the handler may change it; the value `exp` has after the call is the one used from then on). If the returned result is not `digits::more`, return that result at once (no digits are generated).
2. **Integral digits.** While `exp > 0`: take the leading decimal digit `d` of the remaining integral part (the digit of weight `10^(exp-1)`; for the first iteration this is the most significant digit of `I`) and remove it from the remaining integral part. Decrease `exp` by one. Compute `remainder = (remaining integral part << S) + Fr`. Call `on_digit` on the handler with these six arguments, in order: the ASCII character of the digit, the weight of that digit (`10^exp` scaled by `one`), the `remainder`, the `error`, the current `exp`, and `true`. The `error` passed here is the original `error` (it is not scaled in this phase) and `exp` is the already decreased value. If the result is not `digits::more`, return it. (When `exp` was reduced by the handler in step 1 to a value below the number of digits of `I`, the loop simply runs for fewer iterations in the same manner; callers' handlers never do this.)
3. **Fractional digits.** Repeat without a bound until the handler stops it: multiply `Fr` by 10 and `error` by 10; let `d = Fr >> S` (a digit 0 to 9, keeps the original scale) and replace `Fr` by `Fr mod one`; decrease `exp` by one; call `on_digit` on the handler with: the ASCII character of the digit, `one`, the current fractional part `Fr`, the current `error`, the current `exp`, and `false`. If the result is not `digits::more`, return it.

The function returns the first result of the handler that is not `digits::more` (so `done` or `error`). It never returns `more`. On return `exp` has the value it reached (the number of integral digits of `I`, decreased by the number of digits generated, plus any change made by `on_start`): for a value with 3 integral digits that stopped after 5 digits `exp` is `-2`. The digits themselves are only visible through the handler's own state (it stores them).

Example (illustrative): for the number 1234.5 scaled so that `I = 1234` and the fractional part is one half, with a handler that returns `more` four times and then `done`: `on_start` gets divisor `1000 << S`, `exp` becomes 4 at first, then `on_digit('1', 1000 << S, 234.5 << S, ...)` with `exp` 3 and `integral` true, then digits `2`, `3`, `4` with `exp` 2, 1, 0 and divisors `100 << S`, `10 << S`, `1 << S`, the last with `exp` 0; further digits (fractional) would be generated with `integral` false.

## 3. Input specification

- `value`: `fp` as described (`I` non-zero and below 2^32; the original asserts `I != 0`).
- `error`: unsigned 64-bit, small (1 for fixed-precision callers; the width of the rounding interval, scaled, for the shortest-representation caller). Multiplying it by 10 repeatedly in step 3 must not be relied upon not to wrap; handlers stop long before that.
- `exp`: output parameter (its initial value is irrelevant).
- `handler`: object with `on_start` and `on_digit`, called as above; it must eventually return something other than `more`.

## 4. Output specification

Returns a `digits::result` (`done` or `error`). Updates `exp`. No exceptions. All digits are delivered through `handler.on_digit` calls in order.

## 5. Edge cases and constraints

- If `on_start` returns `done` or `error`, no `on_digit` call is made and `exp` keeps the value it had after `on_start`.
- A handler may stop on the very first integral digit; the fractional phase is entered only when all integral digits were consumed and the handler still asked for more.
- The `integral` flag is true exactly for digits of the integral part.
- The function is on the hot path of every floating-point formatting call and must not allocate.
