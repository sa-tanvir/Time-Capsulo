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
