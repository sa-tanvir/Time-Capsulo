```python
def unique_everseen(iterable, key=None):
    seenset = set()
    seenset_add = seenset.add
    seenlist = []
    seenlist_add = seenlist.append
    use_key = key is not None

    for element in iterable:
        k = key(element) if use_key else element
        try:
            if k in seenset:
                continue
            seenset_add(k)
        except TypeError:
            if k in seenlist:
                continue
            seenlist_add(k)
        yield element
```
