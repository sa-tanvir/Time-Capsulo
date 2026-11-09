# Functional specification: `windowed(seq, n, fillvalue=None, step=1)`

## 1. Component overview

A lazy sliding-window utility. Given any iterable, it produces fixed-width
tuples ("windows") of consecutive items, advancing by a configurable stride.
It is a generator: windows are produced on demand and the input is consumed
only as far as needed.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable) that yields tuples.
2. Every yielded tuple has exactly `n` elements.
3. The first window contains the first `n` items of `seq`, in order.
4. Each following window starts `step` items after the previous one.
   With `step=1` this is a classic sliding window: `[1,2,3,4,5]`, `n=3`
   gives `(1,2,3), (2,3,4), (3,4,5)`.
5. If `seq` has fewer than `n` items, exactly one window is produced, filled
   on the right with `fillvalue` (e.g. `[1,2,3]`, `n=4` gives `(1,2,3,None)`).
6. Trailing window: after the last window that is completely filled from
   `seq`, let `p` be the next stride position (the start of the last full
   window plus `step`). One final window starting at position `p`, padded on
   the right with `fillvalue`, is produced **if and only if** `seq` contains
   at least one item that is (a) after the end of the last full window and
   (b) at or after position `p`. Otherwise iteration ends.
   Examples (positions are 0-based):
   - `[1,2,3,4,5,6]`, `n=3`, `fillvalue='!'`, `step=2`: full windows start at
     0 and 2, giving `(1,2,3), (3,4,5)`; item `6` (position 5) is beyond the
     last full window and at or after `p=4`, so `(5,6,'!')` follows.
   - `[1,2,3,4,5]`, `n=3`, `step=2`: full windows `(1,2,3), (3,4,5)`; no item
     lies beyond the last full window, so nothing more is produced.
   - `[1,2,3,4,5]`, `n=3`, `step=1`: full windows `(1,2,3), (2,3,4), (3,4,5)`;
     no trailing window.
   - `[1,2,3,4,5,6,7]`, `n=2`, `step=4`: full windows `(1,2), (5,6)`; item `7`
     is beyond `(5,6)` but before `p=8`, so nothing more is produced.
   - `[1,2,3,4,5,6,7,8,9]`, `n=2`, `step=4`: full windows `(1,2), (5,6)`, then
     `(9, None)` because item `9` sits at `p=8`.
7. The input may be any iterable, including a one-shot iterator; it must be
   iterated at most once.

## 3. Input specification

| Parameter   | Type             | Meaning                                         |
|-------------|------------------|-------------------------------------------------|
| `seq`       | any iterable     | Source items (may be infinite; then output is infinite). |
| `n`         | `int`            | Window width.                                   |
| `fillvalue` | any (default `None`) | Value used to pad incomplete windows.       |
| `step`      | `int` (default `1`) | Distance between the starts of consecutive windows. |

## 4. Output specification

An iterator of tuples of length `n`. Items appear in their original order;
padding (if any) appears only at the right end of a window.

## 5. Edge cases and constraints

- `n < 0`: raise `ValueError` (message: `'n must be >= 0'`). The error is
  raised when iteration starts (the function may be a generator).
- `n == 0`: yield a single empty tuple `()` and stop, regardless of `seq` and
  `step`.
- `step < 1` (with `n > 0`): raise `ValueError` (message: `'step must be >= 1'`).
- Empty `seq` with `n > 0`: yield one window made entirely of `fillvalue`.
- `step` larger than `n`: items between windows are skipped and never
  appear in any window; the trailing-window rule (req. 6) decides whether a
  final padded window is produced.
- Must work on unbounded iterators when only a finite prefix of the output is
  consumed.
