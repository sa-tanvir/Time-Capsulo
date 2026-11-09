# Functional specification

## 1. Component overview

`erase(pos)` removes the element that the iterator `pos` refers to from a `basic_json` value and returns an iterator to the element that followed the removed one. It is the iterator overload of the JSON `erase` family: it works on objects (removing one member), arrays (removing one element) and, for compatibility, on primitive values (where "removing the single element" turns the value into `null`).

## 2. Functional requirements

Let `*this` be the value `erase` is called on and `pos` an iterator (either `iterator` or `const_iterator`).

1. **Ownership check.** `pos` must have been obtained from `*this` (the value it refers to is `*this` itself, by address). Otherwise an `invalid_iterator` exception with id **202** and message `iterator does not fit current value` is thrown. This check is done first, before looking at the type of the value; nothing is modified.
2. **Objects.** The member that `pos` points to is removed from the object. The result is an iterator to the member that follows it in iteration (ascending key) order, or `end()` if it was the last member.
3. **Arrays.** The element that `pos` points to is removed; later elements move one position to the front. The result is an iterator to the element now at that position (the one that followed the removed one), or `end()` if the last element was removed.
4. **Primitive values** (boolean, integer, unsigned integer, floating-point number, string). `pos` must be `begin()` of the value. If so, the value becomes `null` (a string's storage is released) and the result is `end()` of the (now null) value. If `pos` is not `begin()` (for example it is `end()`), an `invalid_iterator` exception with id **205** and message `iterator out of range` is thrown and the value is left unchanged.
5. **Null.** Erasing from a null value (after the ownership check) throws a `type_error` with id **307** and message `cannot use erase() with null`. In general the message is `cannot use erase() with ` followed by the type name of the value (`type_name()`).

## 3. Input specification

- `pos`: an iterator of the type given by the template parameter. For objects and arrays it must be a dereferenceable iterator into `*this` (not `end()`); passing `end()` of a non-empty or empty array or object is outside the contract and is not tested. For primitives, `begin()` is the valid argument, `end()` is rejected as described. An iterator obtained from a different `basic_json` object is rejected (id 202).

## 4. Output specification

- Returns an iterator of the same type as the argument (`IteratorType`) that belongs to `*this`, positioned as described in the rules above (the position follows the removed element; `end()` where stated). The returned iterator is valid for the container type of the value (object, array or primitive).
- Side effect: the value `*this` is modified in place as described. When an exception is thrown, `*this` is unchanged.

## 5. Edge cases and constraints

- Examples: on `[1,2,3]`, `erase(begin())` leaves `[2,3]` and returns an iterator to `2`; `erase(begin()+2)` leaves `[1,2]` and returns `end()`. On `{"a":1,"b":2,"c":3}`, erasing the iterator of `"a"` leaves `{"b":2,"c":3}` and returns the iterator of `"b"`.
- On `5`, `erase(begin())` turns the value into `null` and returns `end()`; `erase(end())` throws id 205. On `"abc"` (a string) the same rules hold and the string is released.
- Exceptions are those listed above (`invalid_iterator` ids 202 and 205, `type_error` id 307); an iterator foreign to the value always gives 202, even when the value is null.
- Erasing from containers invalidates iterators to the removed element (and, for arrays, to everything after it) as for the underlying standard container.
- Memory: a string payload must not leak.
