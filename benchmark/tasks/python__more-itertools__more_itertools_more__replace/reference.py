def replace(iterable, pred, substitutes, count=None, window_size=1):
    """Yield the items from *iterable*, replacing the items for which *pred*
    returns ``True`` with the items from the iterable *substitutes*.

        >>> iterable = [1, 1, 0, 1, 1, 0, 1, 1]
        >>> pred = lambda x: x == 0
        >>> substitutes = (2, 3)
        >>> list(replace(iterable, pred, substitutes))
        [1, 1, 2, 3, 1, 1, 2, 3, 1, 1]

    If *count* is given, the number of replacements will be limited:

        >>> iterable = [1, 1, 0, 1, 1, 0, 1, 1, 0]
        >>> pred = lambda x: x == 0
        >>> substitutes = [None]
        >>> list(replace(iterable, pred, substitutes, count=2))
        [1, 1, None, 1, 1, None, 1, 1, 0]

    Use *window_size* to control the number of items passed as arguments to
    *pred*. This allows for locating and replacing subsequences.

        >>> iterable = [0, 1, 2, 5, 0, 1, 2, 5]
        >>> window_size = 3
        >>> pred = lambda *args: args == (0, 1, 2)  # 3 items passed to pred
        >>> substitutes = [3, 4] # Splice in these items
        >>> list(replace(iterable, pred, substitutes, window_size=window_size))
        [3, 4, 5, 3, 4, 5]

    """
    if window_size < 1:
        raise ValueError('window_size must be at least 1')

    # Save the substitutes iterable, since it's used more than once
    substitutes = tuple(substitutes)

    # Add padding such that the number of windows matches the length of the
    # iterable
    it = chain(iterable, [_marker] * (window_size - 1))
    windows = windowed(it, window_size)

    n = 0
    for w in windows:
        # If the current window matches our predicate (and we haven't hit
        # our maximum number of replacements), splice in the substitutes
        # and then consume the following windows that overlap with this one.
        # For example, if the iterable is (0, 1, 2, 3, 4...)
        # and the window size is 2, we have (0, 1), (1, 2), (2, 3)...
        # If the predicate matches on (0, 1), we need to zap (0, 1) and (1, 2)
        if pred(*w):
            if (count is None) or (n < count):
                n += 1
                yield from substitutes
                consume(windows, window_size - 1)
                continue

        # If there was no match (or we've reached the replacement limit),
        # yield the first item from the window.
        if w and (w[0] is not _marker):
            yield w[0]
