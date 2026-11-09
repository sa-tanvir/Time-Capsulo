You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `SortedDict.update(self, *args, **kwargs)`

## 1. Component overview

`SortedDict` is a mutable mapping that behaves like the built-in `dict` but iterates its keys in
sorted order. It is a `dict` subclass: the items live in the underlying dict, and a sorted list of
the keys (`self._list`, see the context) gives the order. `update` merges new items into the sorted
dict, overwriting values of keys that already exist, and must leave the dict and the sorted key list
consistent. It is also what `SortedDict.__init__` calls (through the alias `_update`) to load the
initial items, so the constructor, `copy`, `fromkeys` and unpickling all depend on it.

## 2. Functional requirements

1. Accept exactly the argument forms of `dict.update`:
   - no arguments (nothing changes);
   - one positional mapping (a `dict`, a `SortedDict`, or any object with `keys()`/`__getitem__`);
   - one positional iterable of key/value pairs (2-item sequences);
   - keyword arguments, alone or together with one positional argument. When a key appears both in
     the positional argument and as a keyword, the keyword's value wins; when a key appears several
     times in an iterable of pairs, the last value wins.
2. After the call, for every new item `(k, v)`: `self[k] == v`. Keys that were already present keep
   their single position in the order and get the new value; keys that were absent are inserted.
   Keys not mentioned are unchanged.
3. After the call the sorted key list holds every dict key exactly once and nothing else, in sorted
   order (by `self._key(k)` when a key function is set). Iteration, `keys()`, `items()`, `values()`,
   positional access (`iloc`, `peekitem`, `popitem`) and `_check()` must all reflect the update.
4. Return `None`.

## 3. Input specification

- `self`: a consistent `SortedDict`, possibly empty, with or without a key function.
- `*args`: zero or one positional argument (mapping or iterable of pairs). More than one positional
  argument is an error, exactly as for `dict.update` (`TypeError`).
- `**kwargs`: extra items; keyword names are strings.
- Keys must be hashable and mutually comparable (or their key-function results must be).

## 4. Output specification

Returns `None`; the effect is the in-place mutation of `self` described above.

Examples (`string.ascii_lowercase` letters mapped to their positions):

```
mapping = [('a', 0), ('b', 1), ..., ('z', 25)]
d = SortedDict()
d.update()                      # still empty
d.update(mapping)               # 26 items
d.update(dict(mapping))         # same items, values overwritten with equal values
d.update(mapping[5:7])          # small update of existing keys
list(d.items()) == mapping      # True

d = SortedDict()
d.update(**dict(mapping))       # keyword form
list(d.items()) == mapping      # True

d = SortedDict({'b': 1})
d.update([('a', 5), ('c', 7), ('a', 6)], c=8)
list(d.items()) == [('a', 6), ('b', 1), ('c', 8)]
```

With a key function (`SortedDict(neg, ...)` where `neg(x) == -x`), keys are ordered by descending
numeric value after the update.

## 5. Edge cases and constraints

- Empty `self`: must still accept every argument form (including keyword-only and empty calls).
- Updating an existing key must never create a second entry for it in the sorted key list.
- If the input contains non-comparable keys, the sorted list raises (`TypeError`); no particular
  partial state is required in that case.
- Arguments that are not a mapping or iterable of pairs raise the same errors as `dict.update`
  (`TypeError` / `ValueError`).
- Input arguments must not be mutated.
- Not thread-safe; no concurrent modification is assumed.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `sortedcontainers/sorteddict.py`
- **Enclosing scope:** `class SortedDict(dict)`

## Imports / includes available in this file

```
import sys
import warnings
from .sortedlist import SortedList, recursive_repr
from .sortedset import SortedSet
```

## Other functions defined in the same file (signatures only; you may call them)

```
__make_raise_attributeerror( original , alternate )
__make_raise_attributeerror.method( self )
_check( self )
_from_iterable( cls , it )
_view_delitem( self , index )
clear( self )
copy( self )
fromkeys( cls , iterable , value = None )
iloc( self )
items( self )
key( self )
keys( self )
peekitem( self , index = - 1 )
pop( self , key , default = __not_given )
popitem( self , index = - 1 )
setdefault( self , key , default = None )
values( self )
```

## Instance state and other members of the enclosing class (you may rely on them)

`SortedDict` subclasses the built-in `dict` (which stores the items) and keeps the dict keys in a
`SortedList` (or `SortedKeyList` when a key function was given). `__init__` caches bound methods:

```
class SortedDict(dict):
    def __init__(self, *args, **kwargs):
        if args and (args[0] is None or callable(args[0])):
            _key = self._key = args[0]
            args = args[1:]
        else:
            _key = self._key = None

        self._list = SortedList(key=_key)

        _dict = super(SortedDict, self)
        self._dict_clear = _dict.clear
        self._dict_delitem = _dict.__delitem__
        self._dict_iter = _dict.__iter__
        self._dict_pop = _dict.pop
        self._dict_setitem = _dict.__setitem__
        self._dict_update = _dict.update

        _list = self._list
        self._list_add = _list.add
        self._list_clear = _list.clear
        self._list_iter = _list.__iter__
        self._list_reversed = _list.__reversed__
        self._list_pop = _list.pop
        self._list_remove = _list.remove
        self._list_update = _list.update
        # (public sorted-list methods such as bisect_left, index, irange, islice are also exposed)

        self._update(*args, **kwargs)

    def __setitem__(self, key, value):
        "Store item `(key, value)` in sorted dict."
        if key not in self:
            self._list_add(key)
        self._dict_setitem(key, value)

    _setitem = __setitem__
    _update = update   # alias defined right after `update` in the class body
```

Invariant between public calls: the set of dict keys equals the contents of `self._list`
(each key exactly once), and `self._list` is sorted (by `self._key(key)` when a key function is set).

=== STUB ===
```python
def update(self, *args, **kwargs):
    raise NotImplementedError  # TODO: implement according to the specification
```
