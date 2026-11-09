```python
def index(self, value, start=None, stop=None):
    _len = self._len

    if not _len:
        raise ValueError('{0!r} is not in list'.format(value))

    if start is None:
        start = 0
    if start < 0:
        start += _len
    if start < 0:
        start = 0

    if stop is None:
        stop = _len
    if stop < 0:
        stop += _len
    if stop > _len:
        stop = _len

    if stop <= start:
        raise ValueError('{0!r} is not in list'.format(value))

    _maxes = self._maxes
    key = self._key(value)
    pos = bisect_left(_maxes, key)

    if pos == len(_maxes):
        raise ValueError('{0!r} is not in list'.format(value))

    _lists = self._lists
    _keys = self._keys
    idx = bisect_left(_keys[pos], key)
    len_keys = len(_keys)
    len_sublist = len(_keys[pos])
    loc = self._loc(pos, idx)

    while loc < stop:
        if _keys[pos][idx] != key:
            break
        if loc >= start and _lists[pos][idx] == value:
            return loc
        loc += 1
        idx += 1
        if idx == len_sublist:
            pos += 1
            if pos == len_keys:
                break
            len_sublist = len(_keys[pos])
            idx = 0

    raise ValueError('{0!r} is not in list'.format(value))
```
