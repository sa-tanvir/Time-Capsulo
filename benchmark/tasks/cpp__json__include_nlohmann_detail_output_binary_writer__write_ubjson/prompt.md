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

`write_ubjson(j, use_count, use_type, add_prefix)` serialises the JSON value `j` in the UBJSON format (Universal Binary JSON, draft 12) to the writer's output sink. It supports the plain form and the "optimized container" forms: containers can carry a count (`#<count>`), and a count together with a common element type (`$<type>#<count>`), in which case the elements are written without type markers.

## 2. Functional requirements

Output is a sequence of characters written to the sink in this order. "Number with marker" means the number is written with the integer or double rule of `write_number_with_ubjson_prefix` (smallest fitting integer type, doubles as `D`) including its marker; "number without marker" omits the marker character.

- **null**: marker `Z` (nothing when `add_prefix` is false).
- **boolean**: `T` for true, `F` for false (nothing when `add_prefix` is false).
- **integer / unsigned / floating-point number**: the number, with its marker if `add_prefix` is true, without otherwise.
- **string**: marker `S` if `add_prefix`; then the byte length of the string as a number *with* marker (integer rule); then the string's bytes unchanged.
- **array**: if `add_prefix`, marker `[`. Then the optimized header:
  - If `use_type` is true and the array is not empty, and all elements have the same marker (`ubjson_prefix` of each element equals that of the first element), the characters `$` and that marker are written and the elements will be written without their markers. (`use_type` is only used together with `use_count`.)
  - If `use_count` is true, `#` followed by the number of elements as a number *with* marker.
  Then each element is written recursively with the same `use_count` and `use_type`; its own marker is included unless the common type was announced with `$`. Finally, if `use_count` is false, the closing marker `]` is written (counted arrays have no closing marker).
- **object**: if `add_prefix`, marker `{`. The optimized header is the same as for arrays, with the common marker computed over all member values (the keys are not considered). Then for each member in key order (ascending, the container's iteration order): the key as its byte length (number with marker) followed by the key's bytes, then the member's value written recursively (its marker omitted if the common type was announced). Finally, if `use_count` is false, the closing marker `}`.
- Other value kinds (discarded) write nothing.

## 3. Input specification

- `j`: any JSON value (null, boolean, integer, unsigned, double, string, array, object), arbitrarily nested; unsigned values above INT64_MAX are outside the contract.
- `use_count`: whether containers carry their element count. `use_type`: whether a common element type is announced; it requires `use_count == true` (calling with `use_type == true` and `use_count == false` is outside the contract).
- `add_prefix`: whether the value's own type marker is written (default `true`). It is `false` only in recursive calls for elements of a typed container.

## 4. Output specification

No return value. The bytes are appended to the output sink in the order described. Numbers are big-endian. For containers written with `use_count == true`, no closing marker is written. Identical elements of a typed container are written back to back with no separators.

## 5. Edge cases and constraints

- `null` gives `5A`; `true` gives `54`; `127` gives `69 7F`; `128` gives `55 80`; `256` gives `49 01 00`; `-129` gives `49 FF 7F`; `1.5` gives `44` followed by the 8-byte big-endian IEEE-754 double; `"ab"` gives `53 69 02 61 62`.
- Plain: `[1,2]` gives `5B 69 01 69 02 5D`. Counted: `[1,2]` gives `5B 23 69 02 69 01 69 02`. Typed: `[1,2]` gives `5B 24 69 23 69 02 01 02`.
- An empty array or object with `use_count` gives `[` `#` `i 0` (`5B 23 69 00`) / `{` `#` `i 0`; `use_type` adds no `$` for an empty container.
- Types are compared by marker: `[1, 200]` has markers `i` and `U`, so it is not typed; `[true, false]` has markers `T` and `F`, so it is not typed; `[true, true]` is typed with `T` and writes no element bytes at all; `[null, null]` likewise with `Z`.
- Objects: `{"a":1}` plain gives `7B 69 01 61 69 01 7D`; with count and type `7B 24 69 23 69 01 69 01 61 01`.
- Containers nested in a typed container have their opening bracket omitted but keep their own header: `[[1],[2]]` with `use_count` and `use_type` gives `5B 24 5B 23 69 02` followed by `24 69 23 69 01 01` and `24 69 23 69 01 02` (each inner array announces its own common type `i`).
- Keys are written with their byte length (not character count) as a number with marker; keys longer than 127 bytes use `U`/`I` as the integer rule says.

=== CONTEXT ===
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

=== STUB ===
```cpp
void write_ubjson(const BasicJsonType& j, const bool use_count,
                  const bool use_type, const bool add_prefix = true)
{
    // TODO: implement according to the specification
}
```
