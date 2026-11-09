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
