# Functional specification: `sort(begin, end, pred)`

## 1. Component overview

Part of pugixml's XPath engine (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). pugixml does not use
`<algorithm>`; this function template is its own in-place sort. It is used to put XPath node-set results into document
order (with `document_order_comparator`). The tests exercise it through XPath queries and
node-set sorting on documents with up to thousands of nodes, in random, reversed and already-sorted arrangements.

## 2. Functional requirements

1. Rearrange the elements of the range `[begin, end)` **in place** so that they are in non-decreasing order with respect to
   `pred`: after the call, for every pair of positions `i < j`, `pred(element[j], element[i])` is `false`.
2. `pred(a, b)` returns `true` when `a` must come **strictly before** `b` (a strict weak ordering, like `std::sort`'s `comp`).
   Elements for which neither `pred(a, b)` nor `pred(b, a)` holds are "equivalent" and may end up in any relative order
   (the sort is not required to be stable). The result is a permutation of the input: no element is lost, duplicated or
   modified.
3. Only element copies (assignment / copy construction) and the predicate may be used on the elements. If you need to
   exchange two elements, the helper `swap(T& lhs, T& rhs)` (see context) exchanges them.
4. The range may be empty or have a single element (nothing happens). Ranges with 2 or more elements must all be sorted
   correctly, including very short ones.
5. `pred` is called with `const` references to elements and must not be called with any other kind of argument; it has no
   side effects. It is passed by `const` reference and may be a stateless functor object.

## 3. Input specification

- `begin`, `end`: iterators of type `I`; in this code base `I` is always a raw pointer `T*` into a contiguous array
  (`xpath_node*` in the library; the tests in this task use `int*` and a small struct pointer), `begin <= end`.
  `end - begin` may be zero.
- `pred`: `const Pred&`, a functor with `bool operator()(const T&, const T&) const`.
- `T` is copy-assignable and copy-constructible; it also has `operator==` available, but equality is not needed for sorting.

## 4. Output specification

No return value. The elements of `[begin, end)` are reordered as described. Elements outside the range are untouched.
No exceptions are thrown by the function itself.

## 5. Edge cases and constraints

- `{}` and `{x}` -> unchanged; `{2, 1}` with `less` -> `{1, 2}`; `{3, 1, 2}` -> `{1, 2, 3}`.
- With `pred(a, b) = (a > b)` the same input ends up in descending order.
- Already sorted, reverse sorted, all-equal, few-distinct-values and "sawtooth" (repeating ramp) inputs of up to a million
  elements are common. The function must run in `O(n log n)` time on all of them (no quadratic behaviour on sorted,
  reversed, all-equal or repetitive inputs) and must not use auxiliary memory proportional to `n` or recursion depth
  proportional to `n` (it runs on the stack of arbitrary callers and the library has no allocator available inside it).
- Ranges of 16 elements or fewer are common (most XPath step results) and should be cheap.
- A predicate that is inconsistent (not a strict weak ordering) is not a supported input.
