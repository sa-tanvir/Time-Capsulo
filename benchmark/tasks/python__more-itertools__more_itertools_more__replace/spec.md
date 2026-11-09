# Functional specification: `replace(iterable, pred, substitutes, count=None, window_size=1)`

## 1. Component overview

A lazy "search and splice" filter for iterables. It scans the input from left
to right, looking at runs of `window_size` consecutive items; whenever a run
satisfies a predicate, those items are removed from the output and the items
of `substitutes` are emitted in their place. All other items pass through
unchanged and in order.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable) over the transformed
   sequence.
2. **Single items (`window_size=1`)**: every item `x` for which `pred(x)` is
   truthy is replaced by all the items of `substitutes` (possibly none, which
   deletes the item). Examples:
   - `replace([1,1,0,1,1,0,1,1], lambda x: x == 0, (2, 3))` gives
     `[1,1,2,3,1,1,2,3,1,1]`.
   - `replace(range(10), lambda x: x % 2 == 0, [])` gives `[1,3,5,7,9]`.
   - `replace(range(5), lambda x: x % 2 == 0, iter('__'))` gives
     `['_','_',1,'_','_',3,'_','_']`. Note that `substitutes` may be a
     one-shot iterator yet its items are emitted at **every** replacement.
3. **Windows (`window_size=k > 1`)**: the scan considers, at the current
   position, the next `k` items, and calls `pred` with them as `k`
   separate positional arguments (`pred(a, b, c)` for `k=3`).
   - If the call is truthy, those `k` items are dropped, the substitutes are
     emitted, and the scan resumes at the item immediately after the matched
     run (matches never overlap).
   - Otherwise the item at the current position is emitted and the scan
     advances by one.
   Example: `replace([0,1,2,5,0,1,2,5], lambda *a: a == (0,1,2), [3,4], window_size=3)`
   gives `[3,4,5,3,4,5]`; with `range(10)` and pattern `(7,8,9)` and no
   substitutes the result is `[0,1,2,3,4,5,6]`.
4. **Near the end of the input**, there is one window for every remaining
   item position, even when fewer than `k` items remain: `pred` is still
   called with exactly `k` arguments, the positions past the end being filled
   with a private placeholder object that compares unequal to ordinary values.
   Such a window can match. Example: `replace(range(4), lambda a,b,c,d,e: True, [5,6,7], window_size=5)`
   gives `[5,6,7]`.
5. **`count`**: if not `None`, at most `count` replacements are performed
   (counting from the left); after that every item passes through unchanged.
   - `replace(range(10), lambda x: x % 2 == 0, [], count=4)` gives
     `[1,3,5,7,8,9]`.
   - `replace(range(10), lambda *a: a in ((0,1,2),(7,8,9)), [], count=1, window_size=3)`
     gives `[3,4,5,6,7,8,9]`.
6. The output is lazy; the input is iterated once. `substitutes` is read
   completely (once) and may be any finite iterable.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `iterable` | iterable | Source items (non-empty for specified behaviour; see §5). |
| `pred` | callable taking `window_size` positional args | Truthy result means "replace this run". |
| `substitutes` | finite iterable | Items emitted for every replacement. |
| `count` | `int` or `None` | Maximum number of replacements; `None` = unlimited. |
| `window_size` | `int >= 1` | Number of consecutive items given to `pred`. |

## 4. Output specification

An iterator over the input items, in order, with each matched run replaced by
the items of `substitutes` (same objects, in their order).

## 5. Edge cases and constraints

- `window_size < 1`: raise `ValueError` (message
  `'window_size must be at least 1'`), at the latest when iteration begins.
- `count=0`: nothing is replaced.
- The behaviour for an empty `iterable` is not specified.
- Arguments are not mutated.
