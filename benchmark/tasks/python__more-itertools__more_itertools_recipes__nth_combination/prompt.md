You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `nth_combination(iterable, r, index)`

## 1. Component overview

Random access into the sequence of `r`-length combinations of a pool of
items. The result is exactly what `list(itertools.combinations(iterable,
r))[index]` would return, but it must be computed directly, without
generating the preceding combinations, so that it stays fast even when the
number of combinations is astronomically large.

## 2. Functional requirements

1. Treat `iterable` as an ordered pool of `n` items (positions matter, values
   are not compared; duplicate values are treated as distinct positions).
2. Consider all combinations of `r` positions out of the `n`, each listed in
   increasing position order, and the whole list ordered lexicographically by
   positions (the order produced by `itertools.combinations`). There are
   `C(n, r)` of them.
3. Return the combination at position `index` in that list, as a `tuple` of
   the corresponding pool items.
4. Negative `index` counts from the end, as with list indexing: `-1` is the
   last combination, `-C(n, r)` the first.
5. Examples:
   - for every `i`, `nth_combination('abcdefg', 4, i) == list(combinations('abcdefg', 4))[i]`;
     e.g. index `0` gives `('a','b','c','d')`, index `34` (the last) gives
     `('d','e','f','g')`.
   - `nth_combination(range(180), 4, 2000000)` gives `(2, 12, 35, 126)`.
   - `nth_combination('abc', 0, 0)` gives `()`.
6. Running time must not grow with `index` or with `C(n, r)` in a way that
   enumerates combinations; it should be polynomial in `n` (Python big
   integers may be needed for the counts).

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `iterable` | finite iterable | The pool; it is consumed once. |
| `r` | `int` | Combination length. |
| `index` | `int` | Position in lexicographic order; may be negative. |

## 4. Output specification

A `tuple` of length `r` containing items of the pool (the original objects),
in pool order.

## 5. Edge cases and constraints

- `r < 0` or `r > n`: raise `ValueError` (no message required). E.g.
  `nth_combination([], -1, 0)` and `nth_combination([], 3, 0)` both raise
  `ValueError`. This check takes precedence over the index check.
- `index` outside `[-C(n,r), C(n,r) - 1]`: raise `IndexError`. E.g.
  `nth_combination('abcdefg', 3, -36)` raises `IndexError` because
  `C(7,3) = 35`.
- `r == 0` (with any `n >= 0`) has exactly one combination, the empty tuple;
  `r == n` has exactly one combination, the whole pool.
- The function is eager (returns a value, not an iterator) and does not
  modify its arguments.

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
iter_except( func , exception , first = None )
ncycles( iterable , n )
nth( iterable , n , default = None )
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
def nth_combination(iterable, r, index):
    raise NotImplementedError  # TODO: implement according to the specification
```
