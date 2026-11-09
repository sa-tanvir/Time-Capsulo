You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `more_itertools/more.py`

## Imports / includes available in this file

```
from collections import Counter, defaultdict, deque
from collections.abc import Sequence
from functools import partial, wraps
from heapq import merge
from itertools import (
    combinations,
    chain,
    compress,
    count,
    cycle,
    dropwhile,
    groupby,
    islice,
    repeat,
    starmap,
    takewhile,
    tee,
    zip_longest,
)
from operator import itemgetter, lt, gt, sub
from sys import maxsize, version_info
from time import monotonic
from .recipes import consume, flatten, powerset, take, unique_everseen
```

## Other functions defined in the same file (signatures only; you may call them)

```
_collate( * iterables , key = lambda a : a , reverse = False )
_get_slice( self , index )
_get_values( self , value )
adjacent( predicate , iterable , distance = 1 )
always_iterable( obj , base_type = ( str , bytes )
always_reversible( iterable )
chunked( iterable , n )
circular_shifts( iterable )
collapse( iterable , base_type = None , levels = None )
collapse.walk( node , level )
collate( * iterables , ** kwargs )
consecutive_groups( iterable , ordering = lambda x : x )
consumer( func )
consumer.wrapper( * args , ** kwargs )
count_cycle( iterable , n = None )
decode( iterable )
difference( iterable , func = sub , * , initial = None )
distinct_combinations( iterable , r )
distinct_permutations( iterable )
distinct_permutations.make_new_permutations( pool , e )
distribute( n , iterable )
divide( n , iterable )
elements( self )
encode( iterable )
exactly_n( iterable , n , predicate = bool )
filter_except( validator , iterable , * exceptions )
first( iterable , default = _marker )
groupby_transform( iterable , keyfunc = None , valuefunc = None )
ichunked( iterable , n )
ilen( iterable )
interleave( * iterables )
interleave_longest( * iterables )
intersperse( e , iterable , n = 1 )
islice_extended( iterable , * args )
iterate( func , start )
last( iterable , default = _marker )
locate( iterable , pred = bool , window_size = None )
lstrip( iterable , pred )
make_decorator( wrapping_func , result_index = 0 )
make_decorator.decorator( * wrapping_args , ** wrapping_kwargs )
make_decorator.make_decorator.decorator.make_decorator.make_decorator.decorator.outer_wrapper.inner_wrapper( * args , ** kwargs )
make_decorator.make_decorator.decorator.outer_wrapper( f )
map_except( function , iterable , * exceptions )
map_reduce( iterable , keyfunc , valuefunc = None , reducefunc = None )
one( iterable , too_short = None , too_long = None )
only( iterable , default = None , too_long = None )
padded( iterable , fillvalue = None , n = None , next_multiple = False )
partitions( iterable )
peek( self , default = _marker )
prepend( self , * items )
replace( iterable , pred , substitutes , count = None , window_size = 1 )
rlocate( iterable , pred = bool , window_size = None )
rstrip( iterable , pred )
seek( self , index )
set_partitions( iterable , k = None )
set_partitions.apply_selection( k )
set_partitions.less( a , b )
set_partitions.part_inds( inds , k , prev )
side_effect( func , iterable , chunk_size = None , before = None , after = None )
sliced( seq , n )
sort_together( iterables , key_list = ( 0 , )
split_after( iterable , pred )
split_at( iterable , pred )
split_before( iterable , pred )
split_into( iterable , sizes )
spy( iterable , n = 1 )
stagger( iterable , offsets = ( - 1 , 0 , 1 )
strip( iterable , pred )
substrings( iterable )
substrings_indexes( seq , reverse = False )
time_limited( limit_seconds , iterable )
unique_to_each( * iterables )
unzip( iterable )
unzip.itemgetter( i )
unzip.unzip.itemgetter.getter( obj )
windowed( seq , n , fillvalue = None , step = 1 )
with_iter( context_manager )
zip_offset( * iterables , offsets , longest = False , fillvalue = None )
```

=== STUB ===
```python
def numeric_range(*args):
    raise NotImplementedError  # TODO: implement according to the specification
```
