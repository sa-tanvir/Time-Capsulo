You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `SortedList._pos(self, idx)`

## 1. Component overview

`SortedList` stores its sorted values split across several sublists (`self._lists`), with extra
bookkeeping described under "Instance state" in the context, including an optional, lazily built
positional index (`self._index`, `self._offset`). `_pos` translates a position in the flat sorted
sequence (what the user passes to `sl[i]`, `del sl[i]`, `sl.pop(i)`, `islice`, `SortedDict.peekitem`,
the `SortedDict` views, ...) into the pair `(pos, idx)` such that the value lives at
`self._lists[pos][idx]`. It is the inverse of `self._loc(pos, idx)`. It is called on every
positional access, so it must be fast: logarithmic in the number of sublists, not a scan over them
(building the positional index once and reusing it is allowed).

## 2. Functional requirements

Let `n = self._len` and let `seq` be the concatenation of all sublists.

1. Accept a non-negative `idx` with `0 <= idx < n` and return the unique pair `(pos, idx_in)` with
   `0 <= pos < len(self._lists)`, `0 <= idx_in < len(self._lists[pos])` and
   `self._lists[pos][idx_in] is seq[idx]` (i.e. `idx` equals the total length of sublists
   `0 .. pos-1` plus `idx_in`).
2. Accept a negative `idx` with `-n <= idx < 0`, meaning `n + idx` as for Python lists, and return the
   pair for that position.
3. Raise `IndexError('list index out of range')` when `idx >= n` or `idx < -n` (this includes any
   index on an empty list).
4. The returned value is a 2-tuple of `int`.
5. Contents and order of the list must not change. If the positional index is empty when needed, it
   may be built by calling `self._build_index()`; a non-empty index is valid and may be used as is.
   All invariants listed in the context must hold afterwards.

## 3. Input specification

- `self`: a valid `SortedList` or `SortedKeyList` (any size, load factor >= 4, any sublist sizes
  allowed by the invariants, positional index built or not).
- `idx`: an `int` (may be negative or far outside the valid range).

## 4. Output specification

A tuple `(pos, idx_in)` as defined above, or a raised `IndexError` with message
`list index out of range`.

Examples (sublists shown explicitly):

```
# self._lists == [[1, 2, 3], [4, 5], [6, 7, 8, 9], [10, 11, 12, 13, 14]], self._len == 14
_pos(0)    -> (0, 0)
_pos(2)    -> (0, 2)
_pos(3)    -> (1, 0)
_pos(8)    -> (2, 3)       # value 9
_pos(13)   -> (3, 4)       # value 14
_pos(-1)   -> (3, 4)
_pos(-5)   -> (3, 0)
_pos(-6)   -> (2, 3)
_pos(-14)  -> (0, 0)
_pos(14)   -> IndexError: list index out of range
_pos(-15)  -> IndexError: list index out of range

SortedList()._pos(0)   -> IndexError
SortedList()._pos(-1)  -> IndexError
```

Through the public API: `SortedList(range(100))[200]` and `[-101]` raise `IndexError`;
`sl.pop(-11)` / `sl.pop(10)` on a 10-element list raise `IndexError`.

## 5. Edge cases and constraints

- Single-sublist lists and lists with many tiny sublists (load factor 4) must both work.
- The answer depends only on the sublist lengths, never on the values.
- Do not modify `self._lists`, `self._maxes` or `self._len`.
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
def _pos(self, idx):
    raise NotImplementedError  # TODO: implement according to the specification
```
