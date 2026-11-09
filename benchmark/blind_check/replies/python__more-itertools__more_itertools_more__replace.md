```python
def replace(iterable, pred, substitutes, count=None, window_size=1):
    if window_size < 1:
        raise ValueError('window_size must be at least 1')

    # Save the substitutes so they can be emitted at every replacement
    substitutes = tuple(substitutes)

    # Pad the end so that every item position gets a full-width window
    marker = object()
    padded_it = chain(iterable, repeat(marker, window_size - 1))
    windows = windowed(padded_it, window_size, fillvalue=marker)

    n = 0
    for w in windows:
        if w[0] is marker:
            # Only possible for an empty input
            break
        if (count is None or n < count) and pred(*w):
            n += 1
            yield from substitutes
            consume(windows, window_size - 1)
        else:
            yield w[0]
```
