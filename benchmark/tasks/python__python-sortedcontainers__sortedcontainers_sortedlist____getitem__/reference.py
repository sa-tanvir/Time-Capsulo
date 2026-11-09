def __getitem__(self, index):
    """Lookup value at `index` in sorted list.

    ``sl.__getitem__(index)`` <==> ``sl[index]``

    Supports slicing.

    Runtime complexity: `O(log(n))` -- approximate.

    >>> sl = SortedList('abcde')
    >>> sl[1]
    'b'
    >>> sl[-1]
    'e'
    >>> sl[2:5]
    ['c', 'd', 'e']

    :param index: integer or slice for indexing
    :return: value or list of values
    :raises IndexError: if index out of range

    """
    _lists = self._lists

    if isinstance(index, slice):
        start, stop, step = index.indices(self._len)

        if step == 1 and start < stop:
            if start == 0 and stop == self._len:
                return reduce(iadd, self._lists, [])

            start_pos, start_idx = self._pos(start)

            if stop == self._len:
                stop_pos = len(_lists) - 1
                stop_idx = len(_lists[stop_pos])
            else:
                stop_pos, stop_idx = self._pos(stop)

            if start_pos == stop_pos:
                return _lists[start_pos][start_idx:stop_idx]

            prefix = _lists[start_pos][start_idx:]
            middle = _lists[(start_pos + 1):stop_pos]
            result = reduce(iadd, middle, prefix)
            result += _lists[stop_pos][:stop_idx]

            return result

        if step == -1 and start > stop:
            result = self._getitem(slice(stop + 1, start + 1))
            result.reverse()
            return result

        # Return a list because a negative step could
        # reverse the order of the items and this could
        # be the desired behavior.

        indices = range(start, stop, step)
        return list(self._getitem(index) for index in indices)
    else:
        if self._len:
            if index == 0:
                return _lists[0][0]
            elif index == -1:
                return _lists[-1][-1]
        else:
            raise IndexError('list index out of range')

        if 0 <= index < len(_lists[0]):
            return _lists[0][index]

        len_last = len(_lists[-1])

        if -len_last < index < 0:
            return _lists[-1][len_last + index]

        pos, idx = self._pos(index)
        return _lists[pos][idx]
