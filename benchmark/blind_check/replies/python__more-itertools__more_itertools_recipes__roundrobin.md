```python
def roundrobin(*iterables):
    iterators = deque(map(iter, iterables))
    while iterators:
        it = iterators.popleft()
        try:
            value = next(it)
        except StopIteration:
            continue
        iterators.append(it)
        yield value
```
