get_cbor_object: none (mostly clear; wrote from knowledge of the original; minor: 0xFF break check relies on get() return value)
get_cbor_string: none significant (chunk nesting for 0x7F handled recursively; EOF in chunk header gives 110 via recursion, matches spec)
get_ubjson_array: minor - spec says 'N' as typed-array type reads no elements, but section 4 also lists 'N' as an unknown type error (112); I followed rule 2 (no elements read)
get_ubjson_object: minor - 'N' as typed-object type is an error 112 (via get_ubjson_value), unlike arrays; typed 'T/F/Z' with count follows get_ubjson_value; had to guess key.clear() placement
lexer_scan: none (token_string reset not mentioned; assumed scan_* routines handle it)
json_pointer_get_unchecked: array_index is said to throw std::invalid_argument but spec requires 109, so I wrapped it in JSON_TRY/JSON_CATCH to rethrow 109; unclear whether std::out_of_range from stoi needs handling (declared out of contract); used public type()/operator[] instead of private members
write_ubjson: none significant; for objects front() and begin()/end() on const json used for common-type check (I used begin()+1 for arrays, begin() for objects since map iterators are not random access); unclear whether keys' prefix should be considered (spec says no)
json_diff: none significant; spec's removal order (largest first) implemented by inserting each removal at the same fixed position; no ambiguity about operator== on mixed numeric types
json_erase: ambiguity - for primitives, the returned end() is computed before the value is turned into null (original behavior); spec says "end() of the now null value" which may differ in primitive_iterator state; ignored
json_erase_pos: same primitive end() timing ambiguity as erase(first,last)
