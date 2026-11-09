# Functional specification: `roundrobin(*iterables)`

## 1. Component overview

A lazy interleaving utility (the classic itertools "roundrobin" recipe). It
takes any number of iterables and yields one item from each in turn, cycling
through them in argument order; iterables that run out are dropped from the
rotation and the remaining ones continue until all are exhausted.

## 2. Functional requirements

1. Return an iterator (a generator is acceptable).
2. Items are produced in rounds. In each round, every iterable that is not yet
   exhausted contributes its next item, in the order the iterables were passed.
3. When an iterable is exhausted it is skipped from then on; the relative
   order of the remaining iterables is unchanged. Iteration ends when all
   iterables are exhausted.
4. Every item of every input appears exactly once in the output, and items
   from the same input keep their original relative order.
5. Examples:
   - `roundrobin('ABC', 'D', 'EF')` gives `['A','D','E','B','F','C']`
   - `roundrobin('ABC', [1,2,3], range(3))` gives
     `['A',1,0,'B',2,1,'C',3,2]`
   - `roundrobin('ABCD', [1,2], range(0))` gives `['A',1,'B',2,'C','D']`
6. The result is lazy: inputs are advanced only as output is requested, one
   item at a time. Each input is iterated at most once (one-shot iterators are
   fine), and an input is never advanced again after it has signalled
   exhaustion. Infinite inputs are allowed (the output is then infinite).

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `*iterables` | zero or more iterables | Sources to interleave; may be of different lengths and types. |

## 4. Output specification

An iterator over all items of all inputs, interleaved round-robin as
described. The yielded objects are the original items (no copies).

## 5. Edge cases and constraints

- No arguments: yields nothing.
- Empty inputs contribute nothing and do not disturb the order of the others.
- A single input: yields its items unchanged.
- Exceptions (other than normal exhaustion) raised by an input propagate.
- The function does not mutate its inputs beyond consuming iterators.
