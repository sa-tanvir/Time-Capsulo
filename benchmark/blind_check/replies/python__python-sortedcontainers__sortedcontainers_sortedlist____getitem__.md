```python
def __getitem__(self, index):
    _lists = self._lists
    _len = self._len

    if isinstance(index, slice):
        start, stop, step = index.indices(_len)

        if step == 1:
            if start >= stop:
                return []
            if start == 0 and stop == _len:
                return [value for sublist in _lists for value in sublist]
            if len(_lists) == 1:
                return _lists[0][start:stop]
            start_pos, start_idx = self._pos(start)
            stop_pos, stop_idx = self._pos(stop - 1)
            if start_pos == stop_pos:
                return _lists[start_pos][start_idx:stop_idx + 1]
            result = _lists[start_pos][start_idx:]
            for pos in range(start_pos + 1, stop_pos):
                result.extend(_lists[pos])
            result.extend(_lists[stop_pos][:stop_idx + 1])
            return result

        indices = range(start, stop, step)
        count = len(indices)
        if count == 0:
            return []

        if step == -1:
            return self._getitem(slice(stop + 1, start + 1))[::-1]

        if step > 0:
            low, high = indices[0], indices[-1]
        else:
            low, high = indices[-1], indices[0]
        span = high - low + 1

        if count * 4 >= span or len(_lists) == 1:
            values = self._getitem(slice(low, high + 1))
            if step > 0:
                return values[::step]
            return values[::-1][::-step]

        _pos = self._pos
        result = []
        for idx in indices:
            pos, offset = _pos(idx)
            result.append(_lists[pos][offset])
        return result

    if not _len or index >= _len or index < -_len:
        raise IndexError('list index out of range')

    if index < 0:
        index += _len

    if index < len(_lists[0]):
        return _lists[0][index]

    last = _lists[-1]
    last_len = len(last)
    if index >= _len - last_len:
        return last[index - (_len - last_len)]

    pos, idx = self._pos(index)
    return _lists[pos][idx]
```
