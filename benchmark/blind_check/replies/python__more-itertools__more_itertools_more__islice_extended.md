```python
def islice_extended(iterable, *args):
    s = slice(*args)
    start, stop, step = s.start, s.stop, s.step
    if step is None:
        step = 1
    if step == 0:
        raise ValueError('step argument must be a non-zero integer or None.')

    it = iter(iterable)

    if step > 0:
        if start is None:
            start = 0

        if start < 0:
            # Need the last -start items, tagged with their 1-based positions
            cache = deque(enumerate(it, 1), maxlen=-start)
            len_iter = cache[-1][0] if cache else 0

            i = max(len_iter + start, 0)
            if stop is None:
                j = len_iter
            elif stop >= 0:
                j = min(stop, len_iter)
            else:
                j = max(len_iter + stop, 0)

            n = j - i
            if n > 0:
                for _, item in islice(cache, 0, n, step):
                    yield item
        elif stop is not None and stop < 0:
            # Skip to start, then delay output by -stop items
            consume(it, start)
            cache = deque(islice(it, -stop), maxlen=-stop)
            for index, item in enumerate(it):
                cached_item = cache.popleft()
                if index % step == 0:
                    yield cached_item
                cache.append(item)
        else:
            yield from islice(it, start, stop, step)
    else:
        if start is not None and start >= 0:
            cache = list(islice(it, start + 1))
            if stop is None or stop >= 0:
                yield from cache[start:stop:step]
            else:
                len_iter = len(cache) + ilen(it)
                j = len_iter + stop
                yield from cache[start:(j if j >= 0 else None):step]
        else:
            if start is None:
                start = -1

            if stop is not None and stop < 0:
                # Only the last -stop items can be selected
                cache = list(deque(it, maxlen=-stop))
                yield from cache[start:stop:step]
            else:
                skipped = 0 if stop is None else ilen(islice(it, stop + 1))
                rest = list(it)
                len_iter = skipped + len(rest)
                i = len_iter + start
                if i >= skipped:
                    yield from rest[i - skipped::step]
```
