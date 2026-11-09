```python
def discard(self, value):
    _maxes = self._maxes

    if not _maxes:
        return

    key = self._key(value)
    pos = bisect_left(_maxes, key)

    if pos == len(_maxes):
        return

    _lists = self._lists
    _keys = self._keys
    idx = bisect_left(_keys[pos], key)
    len_keys = len(_keys)
    len_sublist = len(_keys[pos])

    while True:
        if _keys[pos][idx] != key:
            return
        if _lists[pos][idx] == value:
            self._delete(pos, idx)
            return
        idx += 1
        if idx == len_sublist:
            pos += 1
            if pos == len_keys:
                return
            len_sublist = len(_keys[pos])
            idx = 0
```
