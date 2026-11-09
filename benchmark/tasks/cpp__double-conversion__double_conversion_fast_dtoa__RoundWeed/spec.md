# Functional specification: `RoundWeed(buffer, length, distance_too_high_w, unsafe_interval, rest, ten_kappa, unit)`

## 1. Component overview

Part of the Grisu3 shortest double-to-string conversion in the double-conversion library. Grisu produces the digits of a number that lies somewhere inside an "unsafe" interval around the value `w` being converted, working with fixed-point integers whose error is below one `unit`. `RoundWeed` ("weed out" bad candidates) then tries to improve the candidate held in `buffer` so that it is as close to `w` as possible, and decides whether the candidate can be trusted. It returns `true` when the digits in `buffer` are provably the shortest, closest representation, and `false` when the precision is not sufficient to tell (the caller then falls back to a slower algorithm).

## 2. Functional requirements

All quantities are unsigned 64-bit integers, measured in the same fixed-point unit. `buffer[length - 1]` is the last digit of the candidate; changing that digit by one changes the candidate by `ten_kappa`. `rest` is how far the candidate currently lies below the upper end of the unsafe interval; `distance_too_high_w` is the distance from that upper end down to `w`. Let `small_distance = distance_too_high_w - unit` and `big_distance = distance_too_high_w + unit`.

1. Approach `w` from above as far as possible. While all three of the following hold, decrement the last digit by one (`buffer[length - 1]` becomes the next smaller ASCII digit) and add `ten_kappa` to `rest`:
   - `rest < small_distance`;
   - `unsafe_interval - rest >= ten_kappa` (the decremented candidate is still inside the unsafe interval);
   - either `rest + ten_kappa < small_distance`, or `small_distance - rest >= rest + ten_kappa - small_distance` (one more decrement does not move the candidate farther from `small_distance` than it is now).
2. Then check whether one more decrement would also be acceptable with respect to the other side of `w`, so that two different candidates are both plausible. If all three of the following hold, the closest representation cannot be decided and the function returns `false`:
   - `rest < big_distance`;
   - `unsafe_interval - rest >= ten_kappa`;
   - either `rest + ten_kappa < big_distance`, or `big_distance - rest > rest + ten_kappa - big_distance`.
3. Otherwise return `true` exactly when the candidate is inside the safe interval: `2 * unit <= rest` and `rest <= unsafe_interval - 4 * unit`; return `false` if not.
4. The buffer keeps the decrements made in step 1 whatever the return value is (they are not undone when `false` is returned). Nothing else is modified; `length`, the digits before the last one, and all other arguments are unchanged.

## 3. Input specification

- `buffer`: `Vector<char>` holding at least `length` ASCII digits, `length >= 1`. The caller guarantees that decrementing the last digit as often as step 1 requires never goes below `'0'`.
- `length`: `int`, number of digits in use.
- `distance_too_high_w`, `unsafe_interval`, `rest`, `ten_kappa`, `unit`: `uint64_t`. Preconditions: `rest <= unsafe_interval`, `unit <= distance_too_high_w`, `4 * unit <= unsafe_interval`, `ten_kappa >= 1`, and every value (and sum used above) fits in 63 bits.

## 4. Output specification

`bool` as above; the last digit of `buffer` may be decreased as in step 1.

## 5. Edge cases and constraints

- `ten_kappa` can be a small value such as 1 or 10 as well as a large power of ten multiplied by a power of two.
- The loop in step 1 runs at most 9 times for valid inputs; for each input, the conditions are evaluated in the order given so that no unsigned subtraction wraps around (each subtraction is guarded by the comparison written before it).

Examples (digits before -> digits after, result):

| buffer | distance_too_high_w | unsafe_interval | rest | ten_kappa | unit | result | buffer afterwards |
|---|---|---|---|---|---|---|---|
| `19` | 30 | 40 | 0 | 10 | 1 | true | `16` |
| `19` | 30 | 40 | 5 | 10 | 1 | false | `17` |
| `15` | 12 | 100 | 3 | 10 | 1 | true | `14` |
| `15` | 60 | 100 | 30 | 10 | 1 | true | `12` |
| `123` | 50 | 100 | 20 | 10 | 2 | true | `120` |
| `987` | 10 | 40 | 0 | 10 | 1 | true | `986` |
| `5` | 25 | 45 | 0 | 10 | 1 | false | `3` |
| `5` | 1 | 10 | 2 | 10 | 1 | true | `5` |
| `9` | 5 | 100 | 60 | 10 | 1 | true | `9` |
| `19` | 39 | 40 | 0 | 10 | 1 | false | `15` |
