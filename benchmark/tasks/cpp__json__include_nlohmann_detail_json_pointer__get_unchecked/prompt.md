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

`json_pointer::get_unchecked(ptr)` resolves the JSON pointer (its sequence of reference tokens, RFC 6901) against the JSON value `*ptr` and returns a **mutable reference** to the addressed value. Access is "unchecked" in the sense of `operator[]`: missing object members and array elements are created (as `null`), and `null` values met on the way are turned into containers. It is the lookup used for writing through a JSON pointer (`j[ptr] = value`).

## 2. Functional requirements

Starting with the current value `cur = *ptr`, the tokens are processed in order; after the last token, a reference to `cur` is returned. With no tokens at all (the empty pointer), a reference to `*ptr` itself is returned and nothing is modified.

For each token `t`:

1. **Null values become containers.** If `cur` is `null`, it is first replaced by an empty **array** when `t` consists only of the decimal digits `0`-`9` (this includes the empty token `""`, which has no non-digit character) or when `t` is exactly `"-"`; in every other case it is replaced by an empty **object**. The replacement stays in the document.
2. **Objects.** If `cur` is an object, `cur` becomes the member named `t` (the token is the key, verbatim); if the key is absent, a `null` member with that key is inserted first.
3. **Arrays.**
   - If `t` has more than one character and starts with `'0'`, a parse error is thrown (see below, id 106) before anything is accessed.
   - If `t` is `"-"`, `cur` becomes a newly appended `null` element at the end of the array (index `size()`).
   - Otherwise `t` is converted to an index (decimal integer, parsed as `std::stoi` does; the token must be consumed entirely): the array is extended with `null` elements if the index is at or beyond its size, and `cur` becomes the element at that index. If `t` cannot be parsed as a number at all (for example `"abc"` or `""`), a parse error with id 109 is thrown; if only a prefix of it is a number (for example `"1x"`), an out-of-range error with id 404 is thrown.
4. **Anything else.** If `cur` is a string, boolean or number (not null, object or array), an `out_of_range` error with id 404 is thrown.

Changes already made to the document while walking (created members, appended elements, converted nulls) **remain** when an exception is thrown later in the walk.

## 3. Input specification

- `ptr`: non-null pointer to a `basic_json` value, which is modified in place. May be null-valued, empty containers or arbitrarily nested documents.
- Tokens (the object's `reference_tokens`) are arbitrary strings, already unescaped. Array indices that do not fit in an `int`, and negative numbers such as `"-5"`, are outside the contract (not tested).

## 4. Output specification

A reference to the addressed element, valid until the document is next structurally modified.

Errors (exceptions, with exactly these `what()` messages):

- id 106: `detail::parse_error`, byte position 0: `[json.exception.parse_error.106] parse error: array index '<t>' must not begin with '0'`
- id 109: `detail::parse_error`, byte position 0: `[json.exception.parse_error.109] parse error: array index '<t>' is not a number`
- id 404: `detail::out_of_range`: `[json.exception.out_of_range.404] unresolved reference token '<t>'`

## 5. Edge cases and constraints

- `null` with the pointer `/a/b` becomes `{"a":{"b":null}}` and a reference to the inner `null` is returned; `null` with `/0/1` becomes `[[null,null]]`; `null` with `/-` becomes `[null]`; `null` with `/` (single empty token) becomes an array and then fails with id 109 (the token is not a number).
- `[1,2]` with `/5` becomes `[1,2,null,null,null,null]` and returns the last element; with `/-` it becomes `[1,2,null]`; `/01` throws 106 (the array is unchanged); `/x` throws 109; `/1x` throws 404.
- `{"a":1}` with `/a/b` throws 404 with the token `b` (a number is in the way); with `/b` it becomes `{"a":1,"b":null}`.
- A token `"0"` is valid on an array (only longer tokens starting with `0` are rejected); on an object it is just a key.
- A null reached by an all-digit token is turned into an array even if later tokens are not numbers: `null` with `/00` converts to an array and then throws 106 (the array stays empty).

=== CONTEXT ===
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

=== STUB ===
```cpp
BasicJsonType& get_unchecked(BasicJsonType* ptr) const
{
    // TODO: implement according to the specification
}
```
