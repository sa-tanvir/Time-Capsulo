```python
def iter_except(func, exception, first=None):
    try:
        if first is not None:
            yield first()
        while True:
            yield func()
    except exception:
        pass
```
