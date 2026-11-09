You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `iter_except(func, exception, first=None)`

## 1. Component overview

Adapts a "call until it raises" interface into an iterator. It repeatedly
calls a zero-argument function and yields each result, stopping quietly when
the call raises a designated exception type. It is the exception-based
counterpart of the two-argument form `iter(func, sentinel)`.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable). Nothing is called until
   iteration begins.
2. If `first` is not `None`, it is called once (with no arguments) before
   anything else, and its return value is the first item yielded.
3. Then `func()` is called repeatedly, each return value being yielded, in
   order, one call per item requested.
4. As soon as a call (to `first` or to `func`) raises an exception that is an
   instance of `exception` (which may be a class, a superclass such as
   `Exception`, or a tuple of classes, exactly as in an `except` clause),
   the iterator ends normally; the exception is swallowed and nothing further
   is called.
5. Any other exception propagates to the consumer.
6. Examples:
   - `l = [1, 2, 3]; list(iter_except(l.pop, IndexError))` gives `[3, 2, 1]`
     (and leaves `l` empty).
   - `l = [1, 2, 3]; list(iter_except(l.pop, IndexError, lambda: 25))` gives
     `[25, 3, 2, 1]`.
   - `l = [1, 2]; list(iter_except(l.pop, Exception))` gives `[2, 1]`.
   - `l = [1, 2, 3]; list(iter_except(l.pop, KeyError))` raises `IndexError`
     (after `func` has removed all three items).

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `func` | zero-argument callable | Produces the next value, or raises to signal the end. |
| `exception` | exception class or tuple of classes | What marks the end of iteration. |
| `first` | zero-argument callable or `None` | Optional initial call whose result is yielded first (e.g. a database "first" call). |

## 4. Output specification

An iterator over the values returned by `first()` (if given) followed by the
values returned by successive `func()` calls.

## 5. Edge cases and constraints

- If the very first call raises `exception`, nothing is yielded.
- Side effects of `func`/`first` happen lazily, exactly once per call, and in
  order; the function performs no extra calls (e.g. no look-ahead).
- The function itself mutates nothing; any mutation comes from `func`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `more_itertools/recipes.py`

## Imports / includes available in this file

```
import warnings
from collections import deque
from itertools import (
    chain,
    combinations,
    count,
    cycle,
    filterfalse,
    groupby,
    islice,
    repeat,
    starmap,
    tee,
    zip_longest,
)
import operator
from random import randrange, sample, choice
```

## Other functions defined in the same file (signatures only; you may call them)

```
all_equal( iterable )
consume( iterator , n = None )
dotproduct( vec1 , vec2 )
first_true( iterable , default = None , pred = None )
flatten( listOfLists )
grouper( iterable , n , fillvalue = None )
ncycles( iterable , n )
nth( iterable , n , default = None )
nth_combination( iterable , r , index )
padnone( iterable )
pairwise( iterable )
partition( pred , iterable )
powerset( iterable )
prepend( value , iterator )
quantify( iterable , pred = bool )
random_combination( iterable , r )
random_combination_with_replacement( iterable , r )
random_permutation( iterable , r = None )
random_product( * args , ** kwds )
repeatfunc( func , times = None , * args )
roundrobin( * iterables )
tabulate( function , start = 0 )
tail( n , iterable )
take( n , iterable )
unique_everseen( iterable , key = None )
unique_justseen( iterable , key = None )
```

=== STUB ===
```python
def iter_except(func, exception, first=None):
    raise NotImplementedError  # TODO: implement according to the specification
```
