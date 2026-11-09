# Functional specification: `unique_everseen(iterable, key=None)`

## 1. Component overview

A lazy de-duplication filter. It yields each element of an iterable the first
time an element "equal" to it is encountered, preserving the original order,
and silently drops later duplicates. Equality can be judged on the element
itself or on a derived key. It must accept elements (or keys) that are not
hashable, such as lists.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable) over the elements of
   `iterable`, in their original order, omitting every element that is equal
   to an element already yielded.
   `list(unique_everseen('AAAABBBBCCDAABBB'))` gives `['A','B','C','D']`.
2. When `key` is given, two elements count as duplicates when their keys are
   equal (`key(a) == key(b)`); the element yielded is always the **first**
   element (the original object, not its key) of each group.
   `list(unique_everseen('aAbACCc', key=str.lower))` gives `['a','b','C']`;
   `list(unique_everseen('ABBCcAD', str.lower))` gives `['A','B','C','D']`.
3. Unhashable elements (when `key` is `None`) or unhashable keys must work and
   are compared with `==`:
   `list(unique_everseen(['a',[1,2,3],[1,2,3],'a']))` gives `['a',[1,2,3]]`;
   the same result with `key=lambda x: x`.
   `list(unique_everseen(([1,2],[2,3],[1,2])))` gives `[[1,2],[2,3]]`.
   Hashable and unhashable elements may be mixed in the same input; for
   hashable values equality follows normal Python hashing semantics (e.g.
   `1`, `1.0` and `True` are duplicates of each other).
4. `key` is called exactly once per element, in order.
5. The function is lazy: elements are pulled from `iterable` only as the
   result is iterated, and each yielded element is produced as soon as it is
   read. It works on infinite iterators when only a prefix is consumed.
6. The input is iterated exactly once and is not modified; yielded elements
   are the original objects (identity preserved).

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `iterable` | any iterable | Source elements of any type; may be a one-shot or infinite iterator. |
| `key` | callable or `None` (default) | One-argument function giving the value used for duplicate detection; `None` means the element itself. |

## 4. Output specification

An iterator over a subsequence of the input: the first occurrence of each
distinct element (or key), in input order.

## 5. Edge cases and constraints

- Empty input yields nothing.
- Exceptions raised by `key` or by the input iterator propagate to the caller.
- Hashable inputs should be handled in roughly linear time; unhashable ones may
  be slower (quadratic in the number of distinct unhashable values is
  acceptable).
- Not thread-safe; each call has its own independent "seen" state.
