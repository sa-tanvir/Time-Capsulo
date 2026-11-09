# Functional specification: `numeric_range(*args)`

## 1. Component overview

A generalisation of the built-in `range()` to any ordered numeric-like type
that supports `+`, `*` by an integer, and comparison: `int`, `float`,
`fractions.Fraction`, `decimal.Decimal`, and also `datetime.datetime`
values stepped by a `datetime.timedelta`. It returns a lazy iterator over an
arithmetic progression that stops before reaching `stop`.

## 2. Functional requirements

1. Accepted call forms (same as `range`):
   - `numeric_range(stop)`: start is zero **of the type of `stop`**
     (`type(stop)(0)`), step is the integer `1`.
   - `numeric_range(start, stop)`: step is the integer `1`.
   - `numeric_range(start, stop, step)`.
2. The `n`-th produced value (n = 0, 1, 2, ...) must be exactly equal (same
   type, same value) to the Python expression `start + step * n`; for floats
   this means no rounding drift relative to that expression.
3. With a positive step, values are produced while `value < stop`; with a
   negative step, while `value > stop`. Production stops at the first value
   that fails the test (the progression is monotone).
4. The type of every produced value is the type that `start + step * n`
   naturally has. Examples (all from the tests; type equality is checked):
   - `(4,)` gives `[0, 1, 2, 3]` (ints); `(4.0,)` gives `[0.0, 1.0, 2.0, 3.0]`
   - `(1.0, 4)` gives `[1.0, 2.0, 3.0]`; `(1, 4.0)` gives `[1, 2, 3]` (ints)
   - `(0, 20, 5.0)` gives `[0.0, 5.0, 10.0, 15.0]`; `(0, 10, 3)` gives `[0, 3, 6, 9]`
   - `(0, -5, -1)` gives `[0, -1, -2, -3, -4]`; `(0.0, -5, -1)` gives floats
   - `(3, -1, -1.0)` gives `[3.0, 2.0, 1.0, 0.0]`
   - `(1, 2, Fraction(1, 2))` gives `[Fraction(1,1), Fraction(3,2)]`
   - `(Fraction(2, 1),)` gives `[Fraction(0,1), Fraction(1,1)]`
   - `(Decimal('2.0'),)` gives `[Decimal('0'), Decimal('1')]` (Decimal values)
   - `(datetime(2019,3,29,12,34,56), datetime(2019,3,29,12,37,55), timedelta(minutes=1))`
     gives the three datetimes at 12:34:56, 12:35:56 and 12:36:56.
5. Empty results: `(0,)`, `(0.0,)`, `(1, 0)`, `(1.0, 0.0)` all produce
   nothing.
6. The result is an iterator (lazy, possibly unbounded only if `stop` can
   never be reached, which cannot happen for the numeric types above).

## 3. Input specification

| Form | Types |
|------|-------|
| `stop` | `int`, `float`, `Fraction`, `Decimal` (any type constructible from `0`) |
| `start, stop` | numeric values mutually comparable and addable with an `int` step |
| `start, stop, step` | numeric values, or `datetime` start/stop with `timedelta` step |

## 4. Output specification

An iterator of values `start, start + step, start + 2*step, ...` (each
computed as `start + step * n`), strictly before `stop` in the direction of
`step`.

## 5. Edge cases and constraints

- Zero or more than three arguments: raise `TypeError`
  (message `'numeric_range takes at most 3 arguments, got N'`).
- Step equal to zero (e.g. `(1, 2, 0)` or a zero `timedelta`): raise
  `ValueError` (message `'numeric_range arg 3 must not be zero'`).
- Errors are raised when `numeric_range` is called, or at the latest when
  iteration of the result begins (tests only consume via `list(...)`).
- Arguments are not mutated.
