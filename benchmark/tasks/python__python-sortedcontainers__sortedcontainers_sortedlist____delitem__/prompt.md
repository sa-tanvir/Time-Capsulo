You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `SortedList.__delitem__(self, index)`

## 1. Component overview

`SortedList` is a mutable sequence whose values are always kept in ascending order
(`SortedKeyList`, its subtype ordered by a key function, inherits this method unchanged). Values are
split across several sublists with bookkeeping described under "Instance state" in the context.
`__delitem__` implements `del sl[i]` and `del sl[start:stop:step]`: it removes values by position,
with exactly the semantics of `del` on a Python `list` holding the same sorted values. `SortedSet`
and the `SortedDict` views use it for positional deletion. Deleting a single position must cost
about logarithmic time; deleting a large slice should be efficient too (not one costly removal per
value when most of the list goes away).

## 2. Functional requirements

Let `seq` be the sorted sequence before the call and `n = len(self)`.

1. Integer `index`: remove `seq[index]` (negative indices count from the end). If out of range
   (`index >= n` or `index < -n`, including any index on an empty list) raise
   `IndexError('list index out of range')` and leave the list unchanged.
2. `slice` `index`: remove exactly the values at the positions `range(*index.indices(n))`, i.e. the
   list afterwards equals what `del lst[index]` would leave in a plain list copy `lst` of `seq`.
   Any `start`/`stop`/`step` combination is accepted (`None`, negative, out of range, positive or
   negative step). An empty selection leaves the list unchanged. `del sl[:]` empties the list.
3. A slice with `step == 0` raises `ValueError` (as raised by `slice.indices`) and leaves the list
   unchanged.
4. Return `None`.
5. After the call, all invariants listed in the context hold (`self._check()` passes): `_len`,
   `_maxes` (and `_keys` for key lists) are consistent, every sublist is non-empty and within the
   load-factor bounds, and the positional index is either consistent or empty (to be rebuilt
   lazily). The helpers `self._pos(i)` (flat index -> `(sublist, offset)`), `self._delete(pos, idx)`
   (remove one value and restore invariants), `self._getitem`, `self._clear()` and `self._update()`
   are available.

## 3. Input specification

- `self`: a valid `SortedList`/`SortedKeyList` of any size and load factor (>= 4), index built or not.
- `index`: an `int` or a `slice` object (with `int`/`None` fields).

## 4. Output specification

`None`; the effect is the in-place removal described above.

Examples:

```
sl = SortedList('abcde')
del sl[2]        # SortedList(['a', 'b', 'd', 'e'])
del sl[:2]       # SortedList(['d', 'e'])

sl = SortedList(range(100)); sl._reset(17)
del sl[10:40:1]  # removes 10..39 -> 70 values left
del sl[10:40:-1] # empty selection: no change
del sl[10:40:2]  # removes every other value among positions 10..39
del sl[10:40:-2] # empty selection: no change

sl = SortedList(range(100)); sl._reset(17)
while len(sl): del sl[random_position]; sl._check()   # stays valid down to empty
del SortedList(range(100))[:]                           # -> empty, valid

sl = SortedList(range(10)); del sl[::-3]   # removes 9, 6, 3, 0 -> [1, 2, 4, 5, 7, 8]
del SortedList()[0]                      # -> IndexError
```

## 5. Edge cases and constraints

- Deleting the only value, or the last values of the last sublist, must leave a valid (possibly
  empty) list.
- Small load factors (e.g. 4 or 17) mean many sublists; deletions spanning several sublists must
  keep the load-factor bounds.
- For `SortedKeyList` the keys must be removed together with their values.
- Not thread-safe; iterating the list while deleting is not supported.

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

## Helper contracts used by `__delitem__` (all available on `self`)

- `self._pos(idx)`: `idx` is a flat position, negative allowed (counted from the end). Returns a
  pair `(pos, idx2)` such that the value is `self._lists[pos][idx2]`. Raises
  `IndexError('list index out of range')` when `idx >= len(self)` or `idx < -len(self)` (also for
  any `idx` on an empty list). It may build the positional index (`_index`) as a side effect, which
  is harmless; it never changes the stored values.
- `self._delete(pos, idx)`: removes `self._lists[pos][idx]` (and the matching key for
  `SortedKeyList`), updates `_len`, `_maxes` and the index (or resets it to empty) and restores
  the load-factor bounds (merging/removing sublists as needed). Positions after the removed value
  shift down by one. Returns `None`.
- `self._getitem(index)`: the `SortedList.__getitem__` method (also for `SortedKeyList`). For a
  `slice` it always returns a **new plain Python `list`** of the selected values (never a sorted
  container and never a view; an empty selection gives `[]`); for an `int` it returns the value
  or raises `IndexError('list index out of range')`. It does not modify the object.
- `self._clear()`: removes every value (resets `_len`, `_lists`, `_maxes`, `_index`, `_offset`, and
  `_keys` for key lists); `_load` is kept. Returns `None`.
- `self._update(iterable)`: adds every value of `iterable` (the class's own `update`, so key lists
  compute keys), keeping all invariants. Returns `None`.

=== STUB ===
```python
def __delitem__(self, index):
    raise NotImplementedError  # TODO: implement according to the specification
```
