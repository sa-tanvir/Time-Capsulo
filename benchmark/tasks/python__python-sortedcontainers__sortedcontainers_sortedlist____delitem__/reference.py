def __delitem__(self, index):
    """Remove value at `index` from sorted list.

    ``sl.__delitem__(index)`` <==> ``del sl[index]``

    Supports slicing.

    Runtime complexity: `O(log(n))` -- approximate.

    >>> sl = SortedList('abcde')
    >>> del sl[2]
    >>> sl
    SortedList(['a', 'b', 'd', 'e'])
    >>> del sl[:2]
    >>> sl
    SortedList(['d', 'e'])

    :param index: integer or slice for indexing
    :raises IndexError: if index out of range

    """
    if isinstance(index, slice):
        start, stop, step = index.indices(self._len)

        if step == 1 and start < stop:
            if start == 0 and stop == self._len:
                return self._clear()
            elif self._len <= 8 * (stop - start):
                values = self._getitem(slice(None, start))
                if stop < self._len:
                    values += self._getitem(slice(stop, None))
                self._clear()
                return self._update(values)

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
        pos, idx = self._pos(index)
        self._delete(pos, idx)
