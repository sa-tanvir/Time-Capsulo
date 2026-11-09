# Functional specification

## 1. Component overview

`CharacterReader.cacheString(charBuf, stringCache, start, count)` builds a `String` from a range of a character buffer, re-using a small hash-indexed cache so that repeated short strings (tag and attribute names) are not allocated again.

## 2. Functional requirements

1. If `count` is greater than the constant `maxStringCacheLen` (12), return a new `String` of `charBuf[start .. start+count)`; the cache is neither read nor changed.
2. If `count` is less than 1, return the empty string `""` and leave the cache alone.
3. Otherwise (`1 <= count <= 12`) the result is always a string equal to `charBuf[start .. start+count)`. Additionally the cache `stringCache` (an array of strings whose length is a power of two, 512 in practice) is used as a direct-mapped cache keyed by the content:
   - compute a hash of the range with the same recurrence as `String.hashCode` (`h = 31*h + c` over the characters, starting at 0, with 32-bit int overflow); the slot is `hash & (stringCache.length - 1)`;
   - if the slot is empty, create the string, store it in the slot and return it;
   - if the slot holds a string with exactly the same characters (checked with the helper `rangeEquals(charBuf, start, count, cached)`), return that stored instance, so requesting the same content twice in a row yields the identical (`==`) object;
   - if the slot holds a different string (a collision), create a new string, replace the slot with it, and return it.
4. The buffer is never modified; only `stringCache` slots can change.

## 3. Input specification

`charBuf`: a non-null `char[]`. `stringCache`: a non-null `String[]` with power-of-two length, initially all `null`, shared across many calls. `start`, `count`: ints with `0 <= start` and `start + count <= charBuf.length` whenever `count > 0`; `count` may be 0 or negative (then the empty string is returned, `start` unused).

## 4. Output specification

A `String`. Examples (buffer `"hello world "`): `(0, 5)` returns `"hello"`; calling it again returns the same instance as the first call; `(6, 5)` returns `"world"`; `(0, 0)` returns `""`; with a 13-character range the result is equal to the characters but is a fresh object every time; `(3, -1)` returns `""`.

## 5. Edge cases and constraints

- Called for every token the tokeniser produces, so it must not allocate on cache hits.
- Not thread-safe (the cache is unsynchronised).
