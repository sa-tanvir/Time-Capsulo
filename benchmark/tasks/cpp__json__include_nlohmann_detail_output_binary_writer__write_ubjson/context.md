# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/nlohmann/detail/output/binary_writer.hpp` (nlohmann/json 3.7.2), inside
  `template<typename BasicJsonType, typename CharType> class binary_writer { ... }` in `namespace nlohmann::detail`.
  Headers available: `<algorithm>` (`std::all_of`), `<cassert>`, `<cstdint>`, `<limits>`, `<string>`, `nlohmann/detail/exceptions.hpp`, `nlohmann/detail/output/output_adapters.hpp`, `nlohmann/detail/value_t.hpp`.
- The stub is a **public non-static member function** of `binary_writer`; unqualified names below resolve inside the class. `BasicJsonType` is `nlohmann::json`, `CharType` is `char`.
  `binary_writer` is a friend of `basic_json`, so the private payload members of a `BasicJsonType` value `j` are accessible (see below).

## Instance state of `binary_writer`

```
output_adapter_t<CharType> oa;      // the output sink (shared_ptr to an adapter)
    void oa->write_character(CharType c);                          // appends one character
    void oa->write_characters(const CharType* s, std::size_t length);   // appends `length` characters
static CharType to_char_type(std::uint8_t x);                       // converts a byte value to CharType (use for marker characters, e.g. to_char_type('Z'))
```

## Members of `BasicJsonType` (value `j`) used by the function

```
value_t type() const;      // value_t::null, boolean, number_integer, number_unsigned, number_float, string, array, object, (discarded)
j.m_value.boolean (bool), j.m_value.number_integer (std::int64_t), j.m_value.number_unsigned (std::uint64_t), j.m_value.number_float (double),
j.m_value.string (pointer to std::string), j.m_value.array (pointer to std::vector<BasicJsonType>), j.m_value.object (pointer to std::map<std::string, BasicJsonType>)
const_reference front() const;  const_iterator begin() const;  const_iterator end() const;   // for arrays: the elements; for objects: the member values in key order
```

## Sibling member functions of `binary_writer` that the function may call

```
template<typename NumberType>
void write_number_with_ubjson_prefix(const NumberType n, const bool add_prefix);
    // writes the number n in UBJSON form. If add_prefix is true the type marker comes first. Integers use the smallest fitting type:
    //   'i' int8 (-128..127), 'U' uint8 (128..255), 'I' int16, 'l' int32, 'L' int64, each followed by the big-endian value; unsigned values above INT64_MAX throw
    //   out_of_range 407. Floating-point values (double) are written as 'D' + the 8 bytes big-endian. When add_prefix is false only the value bytes are written.
CharType ubjson_prefix(const BasicJsonType& j) const noexcept;
    // the type marker character that a value would get if it were written with a prefix: 'Z' for null, 'T' / 'F' for true / false, 'i','U','I','l','L' for integers
    // (the same smallest-type rule as above, unsigned values included), 'D' for floating-point numbers, 'S' for strings, '[' for arrays, '{' for objects
```
