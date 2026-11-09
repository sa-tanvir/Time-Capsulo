You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `side_effect(func, iterable, chunk_size=None, before=None, after=None)`

## 1. Component overview

A pass-through iterator for running side effects (logging, progress bars,
writing to a file) while items flow through a pipeline. It yields the items of
`iterable` unchanged, calling `func` on each item (or on each group of
`chunk_size` items) just before the item(s) are yielded, with optional setup
and teardown callbacks that run when iteration starts and when it ends.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable) that yields exactly the
   items of `iterable`, in order, unchanged.
2. **Per item** (`chunk_size is None`): for each item, `func(item)` is called
   once, and then the item is yielded. `func`'s return value is ignored.
   Over `range(10)`, `func` is called 10 times.
3. **Per chunk** (`chunk_size = n`): the input is grouped into consecutive
   lists of `n` items (the last list may be shorter, never empty);
   `func(chunk)` is called once with that list, and then the chunk's items are
   yielded one by one. Example: with `func = lambda c: sums.append(sum(c))`,
   `list(side_effect(func, [0,1,2,3,4,5], 2))` gives `[0,1,2,3,4,5]` and
   `sums == [1, 5, 9]`; over `range(10)` with `chunk_size=2`, `func` is called
   5 times.
4. **`before`**: if given, a zero-argument callable invoked once when
   iteration starts (on the first request for an item, not when
   `side_effect` is called), before anything is read from `iterable`.
5. **`after`**: if given, a zero-argument callable invoked exactly once when
   iteration ends, **whatever the reason**: normal exhaustion, an exception
   raised by the input, by `func`, or by `before` itself, or the iterator being
   closed early.
6. Ordering of effects is strict. Example: `f` is a `StringIO`,
   `func(item)` prints the item to `f` and records `f.getvalue()`,
   `before` prints `'HEADER'` to `f`, `after = f.close`, and the input yields
   `'a'`, `'b'` and then raises `RuntimeError`. Consuming the result raises
   `RuntimeError`, the recorded values are `['HEADER\na\n', 'HEADER\na\nb\n']`,
   and `f` is closed.
7. If `before` raises (e.g. `RuntimeError('ouch')`), that exception
   propagates to the consumer, but `after` is still called (e.g. a file
   passed as `after=f.close` ends up closed).
8. Exceptions from `iterable`, `func`, `before` or `after` are not
   suppressed.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `func` | callable taking one argument | Called with each item, or with each chunk (a `list`). |
| `iterable` | any iterable | Source items; iterated once, lazily. |
| `chunk_size` | `int >= 1` or `None` | Group size for `func`; `None` = per item. |
| `before` | zero-argument callable or `None` | Run once when iteration begins. |
| `after` | zero-argument callable or `None` | Run once when iteration ends, in all cases. |

## 4. Output specification

An iterator yielding the same objects as `iterable`, in the same order.

## 5. Edge cases and constraints

- Empty input: `before` and `after` still run (once each) when the result is
  iterated; `func` is never called.
- In chunk mode, a chunk is read completely from the input before `func` is
  called on it and before its first item is yielded.
- Laziness: in per-item mode, each item is read from the input only when
  requested.
- Inputs are not mutated by the function itself.

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
def side_effect(func, iterable, chunk_size=None, before=None, after=None):
    raise NotImplementedError  # TODO: implement according to the specification
```
