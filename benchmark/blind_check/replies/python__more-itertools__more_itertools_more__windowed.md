```python
def windowed(seq, n, fillvalue=None, step=1):
    if n < 0:
        raise ValueError('n must be >= 0')
    if n == 0:
        yield ()
        return
    if step < 1:
        raise ValueError('step must be >= 1')

    window = deque(maxlen=n)
    append = window.append
    i = n  # number of items still needed before the next window is complete
    for item in seq:
        append(item)
        i -= 1
        if not i:
            i = step
            yield tuple(window)

    size = len(window)
    if size < n:
        # Fewer than n items in total (possibly none): one padded window
        yield tuple(window) + (fillvalue,) * (n - size)
    elif 0 < i < min(step, n):
        # Items remain at or after the next stride position: padded tail
        yield tuple(window)[i:] + (fillvalue,) * i
```
