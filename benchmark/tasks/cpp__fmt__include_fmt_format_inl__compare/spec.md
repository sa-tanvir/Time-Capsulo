# Functional specification: `compare(lhs, rhs)` for `bigint`

## 1. Component overview

`bigint` is fmt's small unsigned arbitrary-precision integer type, used by the exact (slow-path) floating-point printing algorithm. `compare` is the three-way comparison of two such numbers: it tells whether the first is smaller than, equal to or larger than the second.

## 2. Functional requirements

1. Return `-1` if the number `lhs` is smaller than `rhs`, `0` if they are equal and `1` if `lhs` is larger.
2. The numbers are compared by value, where the value of a bigint is `sum of bigits_[i] * 2^(32 * (i + exp_))` as described in the context. The two operands may have different numbers of stored bigits and different `exp_` values (for example `bigint(42) <<= 32` stores one bigit with `exp_` 1 while `bigint(42 * 0x100000001)` stores two bigits with `exp_` 0).
3. Both operands are normalised (see the context), so a number with more total bigits (`num_bigits()`) is always the larger one; for equal total bigit counts the numbers are compared from the most significant bigit downwards, and a number that has additional non-zero lower-order bigits that the other one lacks is the larger one when all the overlapping higher bigits are equal.
4. Neither operand is modified.

Examples (values): `42` and `42` give 0; `42` and `42 << 32` give -1 (and the reverse gives 1); `42` and `43` give -1; `43` and `42` give 1; `42 << 32` and `42 * (2^32 + 1)` give -1; `0` and `0` give 0; `0` and `1` give -1; `2^96` and `2^64` give 1; `10^100` and `10^100` give 0; `10^30 * 7` and `10^30 * 3` give 1.

## 3. Input specification

- `lhs`, `rhs`: bigints with at most 32 bigits stored, normalised as described; their `exp_` can be any non-negative value such that the total stays below about 2^1100.

## 4. Output specification

Returns an `int`: `-1`, `0` or `1` as described. Pure function, no exceptions, no allocation.

## 5. Edge cases and constraints

- Zero versus zero is equal; zero versus any positive number is smaller.
- Normalised numbers have a unique representation, so two equal numbers have the same `exp_` and identical stored bigits (and the reverse).
- Equal numbers require inspecting every stored bigit, so the function is linear in the number of stored bigits in the worst case.
