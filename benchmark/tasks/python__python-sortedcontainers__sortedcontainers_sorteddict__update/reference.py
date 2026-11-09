def update(self, *args, **kwargs):
    """Update sorted dict with items from `args` and `kwargs`.

    Overwrites existing items.

    Optional arguments `args` and `kwargs` may be a mapping, an iterable of
    pairs or keyword arguments. See :func:`SortedDict.__init__` for
    details.

    :param args: mapping or iterable of pairs
    :param kwargs: keyword arguments mapping

    """
    if not self:
        self._dict_update(*args, **kwargs)
        self._list_update(self._dict_iter())
        return

    if not kwargs and len(args) == 1 and isinstance(args[0], dict):
        pairs = args[0]
    else:
        pairs = dict(*args, **kwargs)

    if (10 * len(pairs)) > len(self):
        self._dict_update(pairs)
        self._list_clear()
        self._list_update(self._dict_iter())
    else:
        for key in pairs:
            self._setitem(key, pairs[key])
