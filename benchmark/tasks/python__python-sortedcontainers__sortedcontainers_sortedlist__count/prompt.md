You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `SortedKeyList.count(self, value)`

## 1. Component overview

`SortedKeyList` is a `SortedList` subtype that keeps its values ordered by `self._key(value)`, the
key function given at construction (like `sorted(..., key=...)`). Values whose keys are equal form one
contiguous group; inside a group the values are in no particular order and may differ from each
other (e.g. with `key=lambda x: x % 10`, the values `3`, `13` and `23` share a group). The stored
values and their precomputed keys are kept in parallel sublists (see "Instance state" in the
context). `count` is the sorted-key counterpart of `list.count`: it returns how many stored values
are equal to `value`. It must use the key order to find the relevant group instead of scanning the
whole list: the expected cost is logarithmic in the list size plus the size of the group of values
sharing `value`'s key.

## 2. Functional requirements

1. Compute `k = self._key(value)` (one call is enough; stored keys are already available).
2. Return the number of stored positions whose stored key equals `k` **and** whose stored value
   equals `value` (`==`).
3. Values with a different key are never counted, even if they compare equal to `value`.
4. Values with the same key but not equal to `value` are skipped (they may be interleaved with equal
   ones).
5. The list is not modified (contents, order and internal bookkeeping stay valid).

## 3. Input specification

- `self`: a valid `SortedKeyList` of any size and load factor (>= 4), positional index built or not.
  The key function returns values that are totally ordered with each other.
- `value`: any object accepted by the key function.

## 4. Output specification

A non-negative `int`. Returns `0` for an empty list or when no stored value matches.

Examples (`neg(x) == -x`, `modulo(x) == x % 10`):

```
skl = SortedKeyList([4, 4, 4, 4, 3, 3, 3, 2, 2, 1], key=neg)
skl.count(2)  -> 2

skl = SortedKeyList(key=modulo); skl._reset(7)
skl.count(0)  -> 0
for i in range(100):
    for _ in range(i):
        skl.add(i)
skl.count(i) == i   for every i in range(100)   # e.g. count(13) == 13 although 3, 23, ... share its key

SortedKeyList(range(8), key=modulo).count(9)  -> 0   # key 9 absent
SortedKeyList(range(8), key=modulo).count(18) -> 0   # key 8 absent
SortedKeyList(range(20), key=modulo).count(25) -> 0  # key 5 present, but 25 is not stored
```

## 5. Edge cases and constraints

- Empty list: `0`.
- `value`'s key larger than every stored key, or falling between stored keys: `0`.
- Groups may span several internal sublists (small load factors such as 4 or 7); all matching
  values across sublist boundaries must be counted.
- Never raises for a value whose key is comparable with the stored keys; exceptions raised by the key
  function or by comparisons propagate unchanged.
- Not thread-safe; the list must not be modified concurrently.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `sortedcontainers/sortedlist.py`
- **Enclosing scope:** `class SortedKeyList(SortedList)`

## Imports / includes available in this file

```
from __future__ import print_function
from bisect import bisect_left, bisect_right, insort
from itertools import chain, repeat, starmap
from math import log
from operator import add, eq, ne, gt, ge, lt, le, iadd
from textwrap import dedent
from functools import wraps
from sys import hexversion
```

## Other functions defined in the same file (signatures only; you may call them)

```
__make_cmp( seq_op , symbol , doc )
__make_cmp.comparer( self , other )
_build_index( self )
_check( self )
_delete( self , pos , idx )
_expand( self , pos )
_islice( self , min_pos , min_idx , max_pos , max_idx , reverse )
_loc( self , pos , idx )
_pos( self , idx )
_reset( self , load )
add( self , value )
append( self , value )
bisect_key_left( self , key )
bisect_key_right( self , key )
bisect_left( self , value )
bisect_right( self , value )
clear( self )
copy( self )
count( self , value )
discard( self , value )
extend( self , values )
identity( value )
index( self , value , start = None , stop = None )
insert( self , index , value )
irange( self , minimum = None , maximum = None , inclusive = ( True , True )
irange_key( self , min_key = None , max_key = None , inclusive = ( True , True )
islice( self , start = None , stop = None , reverse = False )
key( self )
pop( self , index = - 1 )
recursive_repr( fillvalue = '...' )
recursive_repr.decorating_function( user_function )
recursive_repr.recursive_repr.decorating_function.wrapper( self )
remove( self , value )
reverse( self )
update( self , iterable )
```


## Instance state and other members of the enclosing class and its bases (you may rely on them)

```
class SortedList(MutableSequence):
    DEFAULT_LOAD_FACTOR = 1000

    def __init__(self, iterable=None, key=None):
        assert key is None
        self._len = 0
        self._load = self.DEFAULT_LOAD_FACTOR
        self._lists = []
        self._maxes = []
        self._index = []
        self._offset = 0
        if iterable is not None:
            self._update(iterable)

    # aliases defined in the class body
    _clear = clear
    _update = update
    _getitem = __getitem__
    bisect = bisect_right
    _bisect_right = bisect_right


class SortedKeyList(SortedList):
    def __init__(self, iterable=None, key=identity):
        self._key = key
        self._len = 0
        self._load = self.DEFAULT_LOAD_FACTOR
        self._lists = []
        self._keys = []
        self._maxes = []
        self._index = []
        self._offset = 0
        if iterable is not None:
            self._update(iterable)

    # aliases defined in the class body
    _clear = clear
    _update = update
    _irange_key = irange_key
    bisect = bisect_right
    _bisect_key_left = bisect_key_left
    bisect_key = bisect_key_right
    _bisect_key_right = bisect_key_right
```

Meaning of the instance attributes (these invariants hold between public calls):

- `_lists`: list of non-empty Python lists ("sublists"). Each sublist is sorted, and the
  concatenation of all sublists, in order, is the whole sorted sequence. Empty container: `[]`.
- `_keys` (`SortedKeyList` only): same shape as `_lists`; `_keys[i][j] == self._key(_lists[i][j])`.
  A sorted-key list is ordered by these keys (ties keep no particular value order).
- `_maxes`: one entry per sublist; `_maxes[i]` is the last element of `_lists[i]`
  (for `SortedKeyList`: the last element of `_keys[i]`).
- `_len`: total number of stored values.
- `_load`: load factor (default 1000, at least 4). Every sublist holds at most `2 * _load`
  values, and every sublist except the last holds at least `_load // 2` values.
- `_index`, `_offset`: an optional positional index. When `_index` is empty, it has not been built
  (calling `self._build_index()` builds it). When non-empty it is a complete binary tree stored as a
  flat list (node `p` has children `2*p+1` and `2*p+2`): `_index[0] == _len`; the leaves
  `_index[_offset + i]` equal `len(_lists[i])` for every sublist `i`, so
  `len(_index) == _offset + len(_lists)`; each internal node `p < _offset` equals the sum of its
  existing children (only the left child if the right one is past the end, and 0 if neither exists).
- Helper semantics: `_loc(pos, idx)` converts a (sublist number, offset in sublist) pair into the
  flat index in the sorted sequence; `_pos(idx)` does the reverse for a non-negative or negative flat
  index; `_delete(pos, idx)` removes the value at that pair and restores all invariants;
  `_expand(pos)` restores invariants after sublist `pos` has grown.

=== STUB ===
```python
def count(self, value):
    raise NotImplementedError  # TODO: implement according to the specification
```
