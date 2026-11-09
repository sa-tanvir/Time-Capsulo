You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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
with_iter( context_manager )
zip_offset( * iterables , offsets , longest = False , fillvalue = None )
```

=== STUB ===
```python
def windowed(seq, n, fillvalue=None, step=1):
    raise NotImplementedError  # TODO: implement according to the specification
```
