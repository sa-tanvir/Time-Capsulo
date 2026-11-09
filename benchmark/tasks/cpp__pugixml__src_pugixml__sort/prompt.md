You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, a function template. The file section it belongs to contains small generic algorithm helpers (`swap`, `min_element`, `reverse`, `unique`, `hash_insert`) used by the XPath code.

## Includes available in this file

```
#include "pugixml.hpp"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include <stdint.h>
```

Do not add includes, helper functions or helper structs. (`<algorithm>` is **not** available.)

## Helpers the function can use

```
#define PUGI__FN                           // function linkage macro; keep it as in the stub

template <typename T> inline void swap(T& lhs, T& rhs)      // exchanges two objects through a temporary copy
{ T temp = lhs; lhs = rhs; rhs = temp; }

struct less        { template <typename T> bool operator()(const T& lhs, const T& rhs) const { return lhs < rhs; } };
struct document_order_comparator { bool operator()(const xpath_node& lhs, const xpath_node& rhs) const; };   // document order of two XPath nodes
```

## Caller (for orientation only)

```
// in xpath_sort(xpath_node* begin, xpath_node* end, xpath_node_set::type_t type, bool rev), for unsorted node sets:
sort(begin, end, document_order_comparator());     // begin/end are xpath_node*
```

=== STUB ===
```cpp
template <typename I, typename Pred> PUGI__FN void sort(I begin, I end, const Pred& pred)
{
    // TODO: implement according to the specification
}
```
