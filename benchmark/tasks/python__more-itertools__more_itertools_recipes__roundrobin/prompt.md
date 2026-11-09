You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `roundrobin(*iterables)`

## 1. Component overview

A lazy interleaving utility (the classic itertools "roundrobin" recipe). It
takes any number of iterables and yields one item from each in turn, cycling
through them in argument order; iterables that run out are dropped from the
rotation and the remaining ones continue until all are exhausted.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable).
2. Items are produced in rounds. In each round, every iterable that is not yet
   exhausted contributes its next item, in the order the iterables were passed.
3. When an iterable is exhausted it is skipped from then on; the relative
   order of the remaining iterables is unchanged. Iteration ends when all
   iterables are exhausted.
4. Every item of every input appears exactly once in the output, and items
   from the same input keep their original relative order.
5. Examples:
   - `roundrobin('ABC', 'D', 'EF')` gives `['A','D','E','B','F','C']`
   - `roundrobin('ABC', [1,2,3], range(3))` gives
     `['A',1,0,'B',2,1,'C',3,2]`
   - `roundrobin('ABCD', [1,2], range(0))` gives `['A',1,'B',2,'C','D']`
6. The result is lazy: inputs are advanced only as output is requested, one
   item at a time. Each input is iterated at most once (one-shot iterators are
   fine), and an input is never advanced again after it has signalled
   exhaustion. Infinite inputs are allowed (the output is then infinite).

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `*iterables` | zero or more iterables | Sources to interleave; may be of different lengths and types. |

## 4. Output specification

An iterator over all items of all inputs, interleaved round-robin as
described. The yielded objects are the original items (no copies).

## 5. Edge cases and constraints

- No arguments: yields nothing.
- Empty inputs contribute nothing and do not disturb the order of the others.
- A single input: yields its items unchanged.
- Exceptions (other than normal exhaustion) raised by an input propagate.
- The function does not mutate its inputs beyond consuming iterators.

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
tabulate( function , start = 0 )
tail( n , iterable )
take( n , iterable )
unique_everseen( iterable , key = None )
unique_justseen( iterable , key = None )
```

=== STUB ===
```python
def roundrobin(*iterables):
    raise NotImplementedError  # TODO: implement according to the specification
```
