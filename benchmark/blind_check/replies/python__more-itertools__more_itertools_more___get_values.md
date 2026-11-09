```python
def _get_values(self, value):
    while True:
        pending = self._cache.get(value)
        if pending:
            yield pending.popleft()
            continue

        while True:
            try:
                item = next(self._it)
            except StopIteration:
                return
            item_value = self._key(item)
            if item_value == value:
                yield item
                break
            elif self._validator(item_value):
                self._cache[item_value].append(item)
```
