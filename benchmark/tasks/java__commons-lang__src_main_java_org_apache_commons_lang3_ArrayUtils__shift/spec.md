# Functional specification

## 1. Component overview

`ArrayUtils.shift(array, startIndexInclusive, endIndexExclusive, offset)` rotates the elements of a range of a `byte[]` **in place**, cyclically, by `offset` positions towards higher indices. Elements pushed past the end of the range re-enter at its start. Elements outside the range are not touched.

## 2. Functional requirements

1. Do nothing (return normally) if `array` is `null`.
2. Do nothing if `startIndexInclusive >= array.length - 1` or `endIndexExclusive <= 0`.
3. Clamp the range: a negative `startIndexInclusive` is treated as `0`; an `endIndexExclusive` larger than `array.length` is treated as `array.length`.
4. Let `n = end - start` for the clamped range. If `n <= 1` do nothing (this includes `end <= start`).
5. Otherwise rotate the range right by `offset`: the element at index `start + i` (`0 <= i < n`) moves to index `start + ((i + offset) mod n)`, where the modulus is taken in the mathematical sense (never negative). Negative `offset` therefore rotates left, `offset` may be any `int` (including `Integer.MIN_VALUE` and `Integer.MAX_VALUE`) and an offset that is a multiple of `n` leaves the array unchanged.
6. The array is modified in place and nothing is returned. No copy of the whole range may be needed: the operation should work with constant extra space and time linear in `n` (performance is measured on arrays of millions of elements).

## 3. Input specification

`array`: `byte[]`, may be `null`. `startIndexInclusive`, `endIndexExclusive`: any `int` (may be out of bounds as described). `offset`: any `int`.

## 4. Output specification

`void`. Examples: `[1,2,3,4,5]`, `shift(1, 3, 1)` -> `[1,3,2,4,5]`; then `shift(1, 4, 2)` -> `[1,2,4,3,5]`; `[1,2,3,4]`, `shift(1, 1, 1)` -> unchanged; `[1,2,3,4]`, `shift(0, 4, 4)` and `shift(0, 4, -4)` -> unchanged; `[1,2,3,4]`, `shift(0, 4, 1)` -> `[4,1,2,3]`; `[1,2,3,4]`, `shift(0, 4, -1)` -> `[2,3,4,1]`; `[1,2,3,4,5,6]`, `shift(-3, 100, 2)` -> `[5,6,1,2,3,4]`; `null` array -> no effect.

## 5. Edge cases and constraints

- No exception is thrown for any index or offset values.
- Not thread-safe (mutates the array).
