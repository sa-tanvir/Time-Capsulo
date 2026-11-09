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
