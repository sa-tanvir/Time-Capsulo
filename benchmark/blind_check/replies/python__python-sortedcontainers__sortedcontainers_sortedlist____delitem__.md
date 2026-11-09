```python
def __delitem__(self, index):
    if isinstance(index, slice):
        _len = self._len
        start, stop, step = index.indices(_len)

        if step == 1 and start < stop:
            if start == 0 and stop == _len:
                self._clear()
                return
            elif _len <= 8 * (stop - start):
                values = self._getitem(slice(None, start))
                if stop < _len:
                    values += self._getitem(slice(stop, None))
                self._clear()
                self._update(values)
                return

        indices = range(start, stop, step)

        # Delete items from greatest index to least so
        # that the indices remain valid throughout iteration.

        if step > 0:
            indices = reversed(indices)

        _pos, _delete = self._pos, self._delete

        for index in indices:
            pos, idx = _pos(index)
            _delete(pos, idx)
    else:
        _len = self._len
        if index >= _len or index < -_len:
            raise IndexError('list index out of range')
        if index < 0:
            index += _len
        pos, idx = self._pos(index)
        self._delete(pos, idx)
```
