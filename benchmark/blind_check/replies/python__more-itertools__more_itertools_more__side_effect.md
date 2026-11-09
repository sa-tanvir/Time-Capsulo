```python
def side_effect(func, iterable, chunk_size=None, before=None, after=None):
    try:
        if before is not None:
            before()

        if chunk_size is None:
            for item in iterable:
                func(item)
                yield item
        else:
            it = iter(iterable)
            for chunk in iter(partial(take, chunk_size, it), []):
                func(chunk)
                yield from chunk
    finally:
        if after is not None:
            after()
```
