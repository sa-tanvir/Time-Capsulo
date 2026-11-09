```python
def numeric_range(*args):
    argc = len(args)
    if argc == 1:
        (stop,) = args
        start = type(stop)(0)
        step = 1
    elif argc == 2:
        start, stop = args
        step = 1
    elif argc == 3:
        start, stop, step = args
    else:
        raise TypeError(
            'numeric_range takes at most 3 arguments, got {}'.format(argc)
        )

    zero = type(step)(0)
    if step == zero:
        raise ValueError('numeric_range arg 3 must not be zero')

    values = (start + step * n for n in count())
    if step > zero:
        return takewhile(partial(gt, stop), values)
    return takewhile(partial(lt, stop), values)
```
