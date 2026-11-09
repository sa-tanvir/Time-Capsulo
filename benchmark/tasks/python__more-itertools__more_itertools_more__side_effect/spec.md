# Functional specification: `side_effect(func, iterable, chunk_size=None, before=None, after=None)`

## 1. Component overview

A pass-through iterator for running side effects (logging, progress bars,
writing to a file) while items flow through a pipeline. It yields the items of
`iterable` unchanged, calling `func` on each item (or on each group of
`chunk_size` items) just before the item(s) are yielded, with optional setup
and teardown callbacks that run when iteration starts and when it ends.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable) that yields exactly the
   items of `iterable`, in order, unchanged.
2. **Per item** (`chunk_size is None`): for each item, `func(item)` is called
   once, and then the item is yielded. `func`'s return value is ignored.
   Over `range(10)`, `func` is called 10 times.
3. **Per chunk** (`chunk_size = n`): the input is grouped into consecutive
   lists of `n` items (the last list may be shorter, never empty);
   `func(chunk)` is called once with that list, and then the chunk's items are
   yielded one by one. Example: with `func = lambda c: sums.append(sum(c))`,
   `list(side_effect(func, [0,1,2,3,4,5], 2))` gives `[0,1,2,3,4,5]` and
   `sums == [1, 5, 9]`; over `range(10)` with `chunk_size=2`, `func` is called
   5 times.
4. **`before`**: if given, a zero-argument callable invoked once when
   iteration starts (on the first request for an item, not when
   `side_effect` is called), before anything is read from `iterable`.
5. **`after`**: if given, a zero-argument callable invoked exactly once when
   iteration ends, **whatever the reason**: normal exhaustion, an exception
   raised by the input, by `func`, or by `before` itself, or the iterator being
   closed early.
6. Ordering of effects is strict. Example: `f` is a `StringIO`,
   `func(item)` prints the item to `f` and records `f.getvalue()`,
   `before` prints `'HEADER'` to `f`, `after = f.close`, and the input yields
   `'a'`, `'b'` and then raises `RuntimeError`. Consuming the result raises
   `RuntimeError`, the recorded values are `['HEADER\na\n', 'HEADER\na\nb\n']`,
   and `f` is closed.
7. If `before` raises (e.g. `RuntimeError('ouch')`), that exception
   propagates to the consumer, but `after` is still called (e.g. a file
   passed as `after=f.close` ends up closed).
8. Exceptions from `iterable`, `func`, `before` or `after` are not
   suppressed.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `func` | callable taking one argument | Called with each item, or with each chunk (a `list`). |
| `iterable` | any iterable | Source items; iterated once, lazily. |
| `chunk_size` | `int >= 1` or `None` | Group size for `func`; `None` = per item. |
| `before` | zero-argument callable or `None` | Run once when iteration begins. |
| `after` | zero-argument callable or `None` | Run once when iteration ends, in all cases. |

## 4. Output specification

An iterator yielding the same objects as `iterable`, in the same order.

## 5. Edge cases and constraints

- Empty input: `before` and `after` still run (once each) when the result is
  iterated; `func` is never called.
- In chunk mode, a chunk is read completely from the input before `func` is
  called on it and before its first item is yielded.
- Laziness: in per-item mode, each item is read from the input only when
  requested.
- Inputs are not mutated by the function itself.
