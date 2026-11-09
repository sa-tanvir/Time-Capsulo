def remove(self, value):
    """Remove `value` from sorted-key list; `value` must be a member.

    If `value` is not a member, raise ValueError.

    Runtime complexity: `O(log(n))` -- approximate.

    >>> from operator import neg
    >>> skl = SortedKeyList([1, 2, 3, 4, 5], key=neg)
    >>> skl.remove(5)
    >>> skl == [4, 3, 2, 1]
    True
    >>> skl.remove(0)
    Traceback (most recent call last):
      ...
    ValueError: 0 not in list

    :param value: `value` to remove from sorted-key list
    :raises ValueError: if `value` is not in sorted-key list

    """
    _maxes = self._maxes

    if not _maxes:
        raise ValueError('{0!r} not in list'.format(value))

    key = self._key(value)
    pos = bisect_left(_maxes, key)

    if pos == len(_maxes):
        raise ValueError('{0!r} not in list'.format(value))

    _lists = self._lists
    _keys = self._keys
    idx = bisect_left(_keys[pos], key)
    len_keys = len(_keys)
    len_sublist = len(_keys[pos])

    while True:
        if _keys[pos][idx] != key:
            raise ValueError('{0!r} not in list'.format(value))
        if _lists[pos][idx] == value:
            self._delete(pos, idx)
            return
        idx += 1
        if idx == len_sublist:
            pos += 1
            if pos == len_keys:
                raise ValueError('{0!r} not in list'.format(value))
            len_sublist = len(_keys[pos])
            idx = 0
