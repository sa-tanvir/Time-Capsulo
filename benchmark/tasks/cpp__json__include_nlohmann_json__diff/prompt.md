You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification

## 1. Component overview

`basic_json::diff(source, target, path)` computes a JSON Patch (RFC 6902) document that transforms the JSON value `source` into the JSON value `target`. The result is itself a JSON value: an array of operation objects. Applying the returned patch to `source` yields `target`. The function does not modify its arguments.

## 2. Functional requirements

The result is built as a JSON array of operations, each an object with the members `"op"`, `"path"` and, where applicable, `"value"`. Paths are JSON Pointer strings (RFC 6901); the pointer of the current position is the argument `path`, and nested positions append `"/" + token` to it.

1. If `source == target` (deep comparison), the result is the empty array `[]`.
2. If the two values have different types (`type()` differs, e.g. an integer versus a string, an array versus an object, a value versus null), the result is one operation: `{"op":"replace","path":<path>,"value":<target>}`. Rule 1 is applied first: numbers of different numeric types that compare equal (for example the integer `1` and the float `1.0`) are equal and give `[]`.
3. If both are primitives of the same type (null, boolean, number, string) and they differ, the result is the single operation `{"op":"replace","path":<path>,"value":<target>}`.
4. If both are arrays:
   - Elements at indices `0 .. min(size)-1` are compared pairwise, in increasing index order, with the same rules recursively, using the path `<path>/<index>` (decimal index, no padding). Their operations are appended to the result in that order.
   - If `source` is longer, for every extra index `i` (`min(size) .. source.size()-1`) a `{"op":"remove","path":"<path>/<i>"}` operation is produced. These removal operations are placed after all operations produced so far and are ordered with the **largest index first** (i.e. in decreasing index order), so that applying them in sequence never invalidates a later index.
   - If `target` is longer, for every extra index `i` (`min(size) .. target.size()-1`) in increasing order, `{"op":"add","path":"<path>/<i>","value":<target[i]>}` is appended after all operations produced so far.
5. If both are objects:
   - First, every member of `source`, in ascending key order (the object's own iteration order): if `target` has the same key, the values are compared recursively with the path `<path>/<escaped key>` and the resulting operations are appended; otherwise `{"op":"remove","path":"<path>/<escaped key>"}` is appended.
   - Then, every member of `target` whose key is absent from `source`, in ascending key order, yields `{"op":"add","path":"<path>/<escaped key>","value":<value>}` appended after the operations above.
   - Keys are escaped as JSON Pointer reference tokens before being appended to the path: every `~` becomes `~0` and every `/` becomes `~1`.

## 3. Input specification

- `source`, `target`: any `basic_json` values (null, booleans, numbers, strings, arrays, objects), nested arbitrarily deep.
- `path`: a string that is already a valid, escaped JSON Pointer (default `""`, meaning the whole document). It is used verbatim as the prefix of every produced path; it is not parsed or validated.

## 4. Output specification

A `basic_json` of type array whose elements are objects. Member order inside each operation object is irrelevant to equality (objects are ordered by key), but the order of the operations in the array is exactly as described above. The `"value"` member is a copy of the corresponding part of `target`.

## 5. Edge cases and constraints

- Two empty arrays, two empty objects, or any two equal values give `[]`.
- Top-level examples: `diff(1, 2)` is `[{"op":"replace","path":"","value":2}]`; `diff(null, false)` is `[{"op":"replace","path":"","value":false}]`; `diff([1,2,3,4], [9,2])` is `[{"op":"replace","path":"/0","value":9},{"op":"remove","path":"/3"},{"op":"remove","path":"/2"}]`; `diff([1], [1,2,3])` is `[{"op":"add","path":"/1","value":2},{"op":"add","path":"/2","value":3}]`.
- Object example: `diff({"a":1,"b":2}, {"a":1,"c":3})` is `[{"op":"remove","path":"/b"},{"op":"add","path":"/c","value":3}]`; with the key `"a/b"` the path segment is `a~1b`, and `""` (empty key) yields the path `"/"`.
- A replaced value inside an array that contains removals: the replace/add/remove operations of the common prefix come first, then the removals (largest index first), then the additions (there are never both removals and additions).
- No errors are raised for valid input; the function is pure and recursion depth equals the nesting depth of the inputs.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/nlohmann/json.hpp` (nlohmann/json 3.7.2), inside `namespace nlohmann { class basic_json { ... } }`.
  The whole header is available to the function: `#include <string>`, `<vector>`, `<cassert>`, and every other
  `nlohmann/detail/**` header the class already includes.
- The stub is a **static member function of `basic_json`**; it stays inside the class, so the unqualified names below
  resolve as in the original code. In the benchmark, `json` is `nlohmann::json` (`basic_json<>` with `std::map` objects, `std::vector` arrays, `std::string` strings, `std::int64_t`, `std::uint64_t`, `double`).

## Types and members visible inside the class

```
using value_t = detail::value_t;          // enum: null, object, array, string, boolean, number_integer, number_unsigned, number_float, discarded
using difference_type = std::ptrdiff_t;
using size_type = std::size_t;
using initializer_list_t = std::initializer_list<detail::json_ref<basic_json>>;

basic_json(const value_t v);              // empty value of the given type, e.g. basic_json(value_t::array) is []
static basic_json object(initializer_list_t init = {});     // basic_json::object({{"k", v}, ...}) builds an object
value_t type() const;                     // dynamic type of the value
size_type size() const;                   // number of elements (array) or members (object)
const_iterator cbegin() const;  const_iterator cend() const;   // for objects: it.key(), it.value(); members iterate in ascending key order
const_iterator find(KeyT&& key) const;    // object lookup; end() if absent
reference operator[](size_type idx);  const_reference operator[](size_type idx) const;      // array element
const_reference operator[](const typename object_t::key_type& key) const;                   // object member (key must exist)
void push_back(basic_json&& val);  void push_back(initializer_list_t init);                 // array append (an init list of {"op", ...} pairs makes an object)
iterator insert(const_iterator pos, const_iterator first, const_iterator last);             // array range insert
iterator insert(const_iterator pos, basic_json&& val);                                      // array insert before pos
iterator begin();  iterator end();
friend bool operator==(const_reference lhs, const_reference rhs);                           // deep comparison
```

`nlohmann::json_pointer<basic_json>` (inside `basic_json` it is named `json_pointer`; it is NOT in namespace `detail`, so write `json_pointer::escape(...)`) is a friend and provides

```
static std::string escape(std::string s);   // RFC 6901 escaping of a reference token: '~' -> "~0", then '/' -> "~1"
```

`std::to_string` is available for converting an index to decimal text.

## Declaration

There is no template line above the stub. The default argument `path = ""` is part of the stub.

=== STUB ===
```cpp
static basic_json diff(const basic_json& source, const basic_json& target,
                       const std::string& path = "")
{
    // TODO: implement according to the specification
}
```
