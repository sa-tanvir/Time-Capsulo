def index(self, value, start=None, stop=None):
    """Return first index of value in sorted-key list.

    Raise ValueError if `value` is not present.

    Index must be between `start` and `stop` for the `value` to be
    considered present. The default value, None, for `start` and `stop`
    indicate the beginning and end of the sorted-key list.

    Negative indices are supported.

    Runtime complexity: `O(log(n))` -- approximate.

    >>> from operator import neg
    >>> skl = SortedKeyList([5, 4, 3, 2, 1], key=neg)
    >>> skl.index(2)
    3
    >>> skl.index(0)
    Traceback (most recent call last):
      ...
    ValueError: 0 is not in list

    :param value: value in sorted-key list
    :param int start: start index (default None, start of sorted-key list)
    :param int stop: stop index (default None, end of sorted-key list)
    :return: index of value
    :raises ValueError: if value is not present

    """
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

    stop -= 1
    _lists = self._lists
    _keys = self._keys
    idx = bisect_left(_keys[pos], key)
    len_keys = len(_keys)
    len_sublist = len(_keys[pos])

    while True:
        if _keys[pos][idx] != key:
            raise ValueError('{0!r} is not in list'.format(value))
        if _lists[pos][idx] == value:
            loc = self._loc(pos, idx)
            if start <= loc <= stop:
                return loc
            elif loc > stop:
                break
        idx += 1
        if idx == len_sublist:
            pos += 1
            if pos == len_keys:
                raise ValueError('{0!r} is not in list'.format(value))
            len_sublist = len(_keys[pos])
            idx = 0

    raise ValueError('{0!r} is not in list'.format(value))
