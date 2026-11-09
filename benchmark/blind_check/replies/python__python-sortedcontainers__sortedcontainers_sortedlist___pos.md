```python
def _pos(self, idx):
    _len = self._len

    if idx < 0:
        if idx < -_len:
            raise IndexError('list index out of range')
        idx += _len
    elif idx >= _len:
        raise IndexError('list index out of range')

    _lists = self._lists
    first_len = len(_lists[0])

    if idx < first_len:
        return 0, idx

    last_len = len(_lists[-1])
    if idx >= _len - last_len:
        return len(_lists) - 1, idx - (_len - last_len)

    if not self._index:
        self._build_index()

    _index = self._index
    _offset = self._offset
    pos = 0

    while pos < _offset:
        child = 2 * pos + 1
        child_len = _index[child]
        if idx < child_len:
            pos = child
        else:
            idx -= child_len
            pos = child + 1

    return pos - _offset, idx
```
