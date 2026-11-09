You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `bucket._get_values(self, value)`

## 1. Component overview

`bucket(iterable, key, validator=None)` splits one source iterable into
several lazily-produced child iterators, one per key value ("bucket").
`bucket[value]` returns the child iterator for `value`; for values accepted by
the validator it is the iterator returned by `_get_values(self, value)`, the
method to implement. The other members of the class are shown in
`context.md`; the object state they rely on is:

- `self._it`: the shared source iterator;
- `self._key`: the key function, applied to a source item to get its bucket;
- `self._cache`: a `collections.defaultdict(deque)` mapping a bucket value to
  the items already pulled from the source for that bucket but not yet
  handed out (oldest first);
- `self._validator`: a one-argument predicate saying which bucket values are
  legitimate (default: everything).

## 2. Functional requirements

1. Return an iterator (normally a generator) that yields, in source order,
   every item `x` of the source with `self._key(x) == value`, each exactly
   once across all child iterators created for that value.
2. Pending items already stored in `self._cache[value]` are handed out first,
   oldest first, and removed from the cache as they are handed out. The cache
   must be consulted on **every** step, not only at creation time, because
   other children (and `__contains__`, which pushes an item back to the
   **front** of `self._cache[value]`) can change it between steps.
3. When no pending item exists for `value`, advance the shared source just far
   enough to find the next item whose key equals `value`, and yield it.
   Every item passed over on the way whose key `k` is accepted by
   `self._validator(k)` is appended to `self._cache[k]` (so other buckets
   can deliver it later, in order). Items whose key is rejected by the
   validator are discarded and must not create a cache entry.
4. When the source is exhausted and nothing is pending for `value`, the child
   iterator ends.
5. Laziness: the source is advanced only when an item is requested from the
   child and nothing is pending; never further than the next match. This
   makes infinite sources usable.
6. Examples (`key = lambda x: 10 * (x // 10)`, source
   `[10, 20, 30, 11, 21, 31, 12, 22, 23, 33]`):
   - `list(D[10])` gives `[10, 11, 12]`; afterwards `list(D[30])` gives
     `[30, 31, 33]`, `list(D[20])` gives `[20, 21, 22, 23]` and `list(D[40])`
     gives `[]`.
   - `10 in D` is `True`, `40 in D` is `False`, `21 in D` is `False`, and
     after these membership tests `next(D[10])` still gives `10`.
   - With source `itertools.count(0)`, `key = lambda x: int(str(x)[0])` and
     `validator = lambda x: 0 < x < 10`: the first three items of `D[1]` are
     `[1, 10, 11]`; afterwards `0` is not a key of `D._cache` (item `0` had a
     rejected key and was discarded).

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `self` | `bucket` instance | Holds the shared state described in §1. |
| `value` | hashable | The bucket value to deliver; compared with `==` to `self._key(item)`. |

## 4. Output specification

An iterator over the source items belonging to bucket `value`, in source
order. Side effects: items of other (valid) buckets read on the way are
appended to their cache queues; delivered items are removed from the
cache.

## 5. Edge cases and constraints

- A bucket that never occurs exhausts the whole source (caching everything
  valid) and yields nothing.
- Several child iterators (for the same or different values) may be
  interleaved arbitrarily; together they never duplicate or lose an item.
- Exceptions raised by the source or by `self._key` propagate.
- Not thread-safe.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `more_itertools/more.py`
- **Enclosing scope:** `class bucket`

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
windowed( seq , n , fillvalue = None , step = 1 )
with_iter( context_manager )
zip_offset( * iterables , offsets , longest = False , fillvalue = None )
```


## Other members of the enclosing class `bucket` (you may rely on them)

```
class bucket:
    def __init__(self, iterable, key, validator=None):
        self._it = iter(iterable)
        self._key = key
        self._cache = defaultdict(deque)
        self._validator = validator or (lambda x: True)

    def __contains__(self, value):
        if not self._validator(value):
            return False

        try:
            item = next(self[value])
        except StopIteration:
            return False
        else:
            self._cache[value].appendleft(item)

        return True

    # def _get_values(self, value):  <- the method to implement

    def __getitem__(self, value):
        if not self._validator(value):
            return iter(())

        return self._get_values(value)
```

=== STUB ===
```python
def _get_values(self, value):
    raise NotImplementedError  # TODO: implement according to the specification
```
