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

`erase(first, last)` removes the half-open range `[first, last)` of elements from a `basic_json` value and returns an iterator to the element that followed the removed range. It is the range overload of the JSON `erase` family: it works on objects (removing several members), arrays (removing several elements) and, for compatibility, on primitive values (where the range covering the single element turns the value into `null`).

## 2. Functional requirements

Let `*this` be the value `erase` is called on and `first`, `last` iterators of the same type (`iterator` or `const_iterator`).

1. **Ownership check.** Both `first` and `last` must have been obtained from `*this` (the value they refer to is `*this` itself, by address). If either one belongs to a different value, an `invalid_iterator` exception with id **203** and message `iterators do not fit current value` is thrown. This check is done first, before looking at the type of the value; nothing is modified.
2. **Objects.** All members in `[first, last)` (in iteration, i.e. ascending key, order) are removed. The result is an iterator to the member that followed the last removed member in iteration order (the member `last` pointed to), or `end()` if the range extended to the end. An empty range (`first == last`) removes nothing and returns an iterator equal to `last`.
3. **Arrays.** All elements in `[first, last)` are removed; later elements move to the front. The result is an iterator to the element now at the position where the range started (the one that followed the removed range), or `end()` if the range extended to the end. An empty range removes nothing and returns an iterator at the position of `first`.
4. **Primitive values** (boolean, integer, unsigned integer, floating-point number, string). The range must be exactly `[begin(), end())`: `first` must be `begin()` and `last` must be `end()`. If so, the value becomes `null` (a string's storage is released) and the result is `end()` of the now null value. Otherwise an `invalid_iterator` exception with id **204** and message `iterators out of range` is thrown and the value is left unchanged.
5. **Null.** Erasing from a null value (after the ownership check) throws a `type_error` with id **307** and message `cannot use erase() with null`. In general the message is `cannot use erase() with ` followed by the type name of the value (`type_name()`).

## 3. Input specification

- `first`, `last`: iterators of the type given by the template parameter, both into `*this`, with `first` not after `last`. For objects and arrays both may be any position from `begin()` to `end()` inclusive, as long as `[first, last)` is a valid range (ranges where `first` is after `last` are outside the contract and not tested). Iterators from a different `basic_json` object are rejected (id 203), as soon as any one of the two does not belong to `*this`.

## 4. Output specification

- Returns an iterator of the same type as the arguments (`IteratorType`) that belongs to `*this`, positioned as described in the rules above (the position following the removed range; `end()` where stated).
- Side effect: the value `*this` is modified in place as described. When an exception is thrown, `*this` is unchanged.

## 5. Edge cases and constraints

- Examples: on `[1,2,3]`, `erase(begin(), begin()+2)` leaves `[3]` and returns an iterator to `3`; `erase(begin()+1, end())` leaves `[1]` and returns `end()`; `erase(begin()+1, begin()+1)` leaves `[1,2,3]` and returns an iterator to `2`. On `{"a":1,"b":2,"c":3}`, erasing from the iterator of `"a"` up to (excluding) the iterator of `"c"` leaves `{"c":3}` and returns the iterator of `"c"`.
- On `5`, `erase(begin(), end())` turns the value into `null` and returns `end()`; `erase(begin(), begin())` and `erase(end(), end())` throw id 204. On a string the same rules hold.
- Exceptions are those listed above (`invalid_iterator` ids 203 and 204, `type_error` id 307); a foreign iterator always gives 203, even when the value is null.
- Erasing from containers invalidates iterators to the removed elements (and, for arrays, to everything after the range) as for the underlying standard container.
- Memory: a string payload must not leak.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/nlohmann/json.hpp` (nlohmann/json 3.7.2), inside `class basic_json` (namespace `nlohmann`).
  The whole header is available: `<string>`, `<memory>`, `<cassert>`, the `nlohmann/detail/**` headers, `JSON_THROW`, `JSON_HEDLEY_*` macros, etc.
- The stub is a **public non-static member function** of `basic_json`; the unqualified names below resolve inside the class. In the benchmark `basic_json` is `nlohmann::json`
  (`std::map` objects, `std::vector` arrays, `std::string` strings).

## Declaration lines preceding the stub

The following lines stand directly above the stub in the source file and are NOT part of your answer (do not repeat them):

```
template<class IteratorType, typename std::enable_if<
             std::is_same<IteratorType, typename basic_json_t::iterator>::value or
             std::is_same<IteratorType, typename basic_json_t::const_iterator>::value, int>::type
         = 0>
```

So `IteratorType` is either `basic_json::iterator` or `basic_json::const_iterator`.

## Instance state of `basic_json` (members the function reads or writes)

```
value_t m_type;        // dynamic type: value_t::null, object, array, string, boolean, number_integer, number_unsigned, number_float, (discarded)
json_value m_value;    // union holding the payload:
                       //   object_t*  object;   (object_t = std::map<std::string, basic_json>)
                       //   array_t*   array;    (array_t  = std::vector<basic_json>)
                       //   string_t*  string;   (string_t = std::string; heap allocated with AllocatorType<string_t>)
                       //   boolean_t boolean; number_integer_t number_integer; number_unsigned_t number_unsigned; number_float_t number_float;
void assert_invariant() const noexcept;   // debug-only consistency check of m_type / m_value; call after changing m_type
template<typename T> using AllocatorType = std::allocator<T>;   // class template parameter of basic_json
iterator end();  const char* type_name() const noexcept;  bool is_string() const noexcept;
```

A string payload is owned through `m_value.string` (allocated with `AllocatorType<string_t>`: constructed, then released through
`std::allocator_traits<AllocatorType<string_t>>::destroy` and `::deallocate`).
Other primitive types hold their payload inline in `m_value` and need no cleanup.

## Iterator internals (`detail::iter_impl<basic_json>`; `iterator` and `const_iterator` are friends of / accessible from `basic_json`)

```
pointer m_object;                       // the basic_json value the iterator was obtained from (compare with `this`)
internal_iterator<basic_json> m_it;     // the position, depending on the type of *m_object:
    typename object_t::iterator object_iterator;       // objects (std::map iterator)
    typename array_t::iterator  array_iterator;        // arrays  (std::vector iterator)
    primitive_iterator_t        primitive_iterator;    // every other type (null, boolean, numbers, string):
        constexpr bool is_begin() const noexcept;      //   true when the iterator is begin() (the single element)
        constexpr bool is_end() const noexcept;        //   true when the iterator is end()
```

For a primitive value (including strings) `begin()` is the position of the single element and `end()` is one past it; for null, `begin() == end()`.
`m_it` holds an iterator valid for the container of the matching type only (a default-constructed one for the other kinds).

## Exceptions

```
JSON_THROW(x)   // throws x
detail::invalid_iterator::create(int id, const std::string& what_arg)   // exception whose what() is "[json.exception.invalid_iterator.<id>] <what_arg>"
detail::type_error::create(int id, const std::string& what_arg)         // exception whose what() is "[json.exception.type_error.<id>] <what_arg>"
```

=== STUB ===
```cpp
IteratorType erase(IteratorType first, IteratorType last)
{
    // TODO: implement according to the specification
}
```
