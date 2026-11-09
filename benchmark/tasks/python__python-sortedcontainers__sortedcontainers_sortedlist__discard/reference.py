def discard(self, value):
    """Remove `value` from sorted-key list if it is a member.

    If `value` is not a member, do nothing.

    Runtime complexity: `O(log(n))` -- approximate.

    >>> from operator import neg
    >>> skl = SortedKeyList([5, 4, 3, 2, 1], key=neg)
    >>> skl.discard(1)
    >>> skl.discard(0)
    >>> skl == [5, 4, 3, 2]
    True

    :param value: `value` to discard from sorted-key list

    """
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
