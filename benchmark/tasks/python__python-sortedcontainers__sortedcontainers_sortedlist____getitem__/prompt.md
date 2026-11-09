You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `SortedList.__getitem__(self, index)`

## 1. Component overview

`SortedList` is a sequence whose values are always kept in ascending order (`SortedKeyList`, its
subtype, orders by a key function and inherits this method unchanged). The values are split across
several sublists with bookkeeping described under "Instance state" in the context. `__getitem__`
implements `sl[i]` and `sl[start:stop:step]` with exactly the semantics of a Python `list` holding the
same sorted values. It is also reachable as `self._getitem` and is used by `SortedSet` indexing,
the `SortedDict` keys/items/values views, `SortedDict.peekitem`, and slice deletion. Positional
lookups must be fast: logarithmic in the size for a single index, and proportional to the output
length (not the list length) for slices.

## 2. Functional requirements

Let `seq` be the sorted sequence (concatenation of the sublists) and `n = len(self)`.

1. Integer `index`: return `seq[index]`. Negative indices count from the end (`-1` is the last value).
   Out of range (`index >= n` or `index < -n`, including every index on an empty list): raise
   `IndexError` with the message `list index out of range`.
2. `slice` `index`: return a **new plain `list`** equal to `seq[index]` as Python list slicing would
   produce it, for every combination of `start`, `stop`, `step` (each may be `None`, negative, or out
   of range; they are normalised like `slice.indices(n)`):
   - positive steps give values in ascending order, negative steps in descending order;
   - empty selections give `[]`;
   - a full slice `sl[:]` returns a list of all values (a fresh list, never an internal sublist).
3. A slice with `step == 0` raises `ValueError` (the same error `slice.indices` raises: `slice step
   cannot be zero`).
4. Returned lists must never alias internal storage: mutating the result must not affect the sorted
   list.
5. The method does not change the list's contents. It may build the lazy positional index (the helper
   `self._pos(i)` maps a flat index to a `(sublist, offset)` pair and builds it if needed); all
   invariants in the context must still hold afterwards.

## 3. Input specification

- `self`: a valid `SortedList`/`SortedKeyList` of any size and load factor (>= 4), index built or not.
- `index`: an `int` or a `slice` object (with `int`/`None` fields).

## 4. Output specification

A single stored value for an integer index; a new `list` for a slice.

Examples:

```
sl = SortedList('abcde')
sl[1]      -> 'b'
sl[-1]     -> 'e'
sl[2:5]    -> ['c', 'd', 'e']
sl[::-2]   -> ['e', 'c', 'a']
sl[4:1:-1] -> ['e', 'd', 'c']
sl[3:1]    -> []

sl = SortedList(range(4))
sl[a:b:c] == list(range(4))[a:b:c]
    for a, b in [-6, -4, -2, 0, 2, 4, 6] and c in [-3, -2, -1, 1, 2, 3]

SortedList(range(100))[::0]   -> ValueError
SortedList()[5]               -> IndexError
SortedList(range(100))[200]   -> IndexError
SortedList(range(100))[-101]  -> IndexError
```

## 5. Edge cases and constraints

- Very small load factors (e.g. 4 or 17) produce many sublists; slices spanning many sublists, or
  starting/ending exactly on sublist boundaries, must be correct.
- Index `0` and `-1` on a non-empty list are the minimum and maximum values.
- For `SortedKeyList`, returned objects are the stored values (not their keys).
- Not thread-safe; the list must not be modified concurrently.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `sortedcontainers/sortedlist.py`
- **Enclosing scope:** `class SortedList(MutableSequence)`

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
def __getitem__(self, index):
    raise NotImplementedError  # TODO: implement according to the specification
```
