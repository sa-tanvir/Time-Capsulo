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
