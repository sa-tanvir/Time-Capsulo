# Functional specification: `islice_extended(iterable, *args)`

## 1. Component overview

A lazy slicing utility for arbitrary iterables, extending the standard
library's `itertools.islice` so that `start`, `stop` and `step` may be
negative, exactly like slicing a Python list. It works on one-shot iterators
(and, where the slice allows it, on infinite iterators) and returns an
iterator over the selected items.

## 2. Functional requirements

1. The positional arguments after `iterable` are interpreted exactly like the
   arguments of the built-in `slice(...)`:
   - one argument: `stop`;
   - two arguments: `start, stop`;
   - three arguments: `start, stop, step`.
   Any of them may be `None`.
2. For every finite iterable `xs` and every combination of `start`, `stop`
   (any integer, positive, negative, beyond either end, or `None`) and
   non-zero `step` (positive or negative, or `None`), the items produced must
   be exactly `list(xs)[slice(start, stop, step)]`, in the same order.
   Examples with `xs = ['0','1','2','3','4','5']`:
   - `(-4, -1)` gives `['2','3','4']`
   - `(1, None, 2)` gives `['1','3','5']`
   - `(None, None, -1)` gives the list reversed
   - `(4, 1, -2)` gives `['4','2']`
   - `(10, 20)` and `(-1, -5)` give `[]`
   - `(-10, 3)` gives `['0','1','2']`
3. The input is iterated at most once; it may be a one-shot iterator.
4. Memory use should be bounded by what the slice needs: when the slice can be
   resolved without seeing the end of the input (e.g. non-negative start/stop
   with positive step, or a negative step whose `start` and `stop` are both
   non-negative), the function must work on infinite iterators. Example:
   `list(islice_extended(count(), 110, 99, -2))` gives
   `[110, 108, 106, 104, 102, 100]`. Example with an iterator:
   `list(islice_extended(iter('abcdefgh'), -4, -1))` gives `['e','f','g']`.
5. The result is lazy (a generator is acceptable): no item is consumed from the
   input before iteration of the result begins.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `iterable` | any iterable | Source items; may be a one-shot iterator; may be infinite when the slice permits (req. 4). |
| `*args` | 1 to 3 values, each `int` or `None` | `stop` / `start, stop` / `start, stop, step`, with list-slicing semantics. |

## 4. Output specification

An iterator yielding the selected items of `iterable` (the objects themselves,
not copies), in slice order (descending source position for negative steps).

## 5. Edge cases and constraints

- `step == 0`: raise `ValueError` (message
  `'step argument must be a non-zero integer or None.'`). The error may be
  raised either immediately or when iteration of the result begins; tests
  only check that `list(islice_extended(...))` raises `ValueError`.
- `step=None` means `1`.
- Empty input: yields nothing for any valid slice.
- Indices beyond the input length are clipped as in list slicing (never an
  `IndexError`).
- Slices whose bounds select nothing (e.g. `start >= stop` with a positive
  step) yield nothing.
- Negative `start` with positive step, or negative `stop` with positive step,
  require knowing where the input ends; such slices on infinite inputs need not
  terminate.
