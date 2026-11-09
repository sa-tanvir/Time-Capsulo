# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/nlohmann/detail/json_pointer.hpp` (nlohmann/json 3.7.2), inside
  `template<typename BasicJsonType> class json_pointer { ... }` in `namespace nlohmann`.
  Available headers: `<algorithm>`, `<cctype>`, `<string>`, `<vector>`, `nlohmann/detail/exceptions.hpp`, `nlohmann/detail/value_t.hpp`, `nlohmann/detail/macro_scope.hpp` (`JSON_THROW`, `JSON_TRY`, `JSON_CATCH`, `JSON_HEDLEY_*`).
- The stub is a `const` member function of `json_pointer`. `BasicJsonType` is `nlohmann::basic_json<>` (called `json` below): objects are `std::map<std::string, json>`, arrays `std::vector<json>`.
  `json_pointer` is a friend of `basic_json`, so private members of `basic_json` are accessible.

## Instance state of `json_pointer`

```
std::vector<std::string> reference_tokens;   // the already unescaped reference tokens of the pointer, in order;
                                             // the pointer "/a/0/b" has the tokens {"a", "0", "b"}; the whole-document pointer "" has no tokens;
                                             // the pointer "/" has the single token "" (empty string)
static int array_index(const std::string& s);
    // converts a reference token to an array index: parses a decimal integer with std::stoi semantics
    // (std::invalid_argument if nothing can be parsed, std::out_of_range if the number does not fit an int)
    // and throws detail::out_of_range with id 404 and message "unresolved reference token '<s>'" if the token was not consumed entirely
```

## Members of `BasicJsonType` (json) used by the function

```
detail::value_t type() const;                     // value_t::null, object, array, string, boolean, number_integer, number_unsigned, number_float, discarded
bool is_null() const;
size_type size() const;                           // number of elements of an array / members of an object
json& operator=(json other);   json(detail::value_t t);   // json(value_t::array) is [] and json(value_t::object) is {}; assigning a value_t converts implicitly
reference operator[](size_type idx);              // array access; appends null elements when idx >= size(); on null it first becomes an array
reference operator[](const typename object_t::key_type& key);   // object access; inserts a null member if the key is absent; on null it first becomes an object
```

`size_type` is `std::size_t`.

## Exceptions (`namespace nlohmann::detail`)

```
JSON_THROW(x)                                                      // throws x
parse_error::create(int id, std::size_t byte, const std::string& what_arg)   // what() == "[json.exception.parse_error.<id>] parse error: <what_arg>" (byte 0 adds no position)
out_of_range::create(int id, const std::string& what_arg)          // what() == "[json.exception.out_of_range.<id>] <what_arg>"
JSON_TRY { ... } JSON_CATCH(std::invalid_argument&) { ... }        // try / catch(std::invalid_argument&)
```
