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
