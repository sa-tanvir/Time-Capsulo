You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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
numeric_range( * args )
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
def islice_extended(iterable, *args):
    raise NotImplementedError  # TODO: implement according to the specification
```
