```python
def nth_combination(iterable, r, index):
    pool = tuple(iterable)
    n = len(pool)
    if (r < 0) or (r > n):
        raise ValueError

    # c = C(n, r)
    c = 1
    k = min(r, n - r)
    for i in range(1, k + 1):
        c = c * (n - k + i) // i

    if index < 0:
        index += c

    if (index < 0) or (index >= c):
        raise IndexError

    result = []
    while r:
        # Number of combinations that start with pool[-n]
        c, n, r = c * r // n, n - 1, r - 1
        while index >= c:
            # Skip pool[-1 - n]: drop all combinations starting with it
            index -= c
            c, n = c * (n - r) // n, n - 1
        result.append(pool[-1 - n])

    return tuple(result)
```
