# Functional specification

## 1. Component overview

`JsonTreeReader.peek()` returns the type of the next token of the JSON document being read from a `JsonElement` tree, without consuming it (the `JsonReader` pull-parser contract). It is also the place where the reader steps into the next element of an array.

## 2. Functional requirements

Look at the state of the reader's nesting stack (see "Instance state") and return a `JsonToken`:

1. Stack empty (`stackSize == 0`): `END_DOCUMENT`.
2. The top entry is an **iterator** (the reader is inside a container, between values):
   - The container is the entry just below the iterator on the stack. If it is a `JsonObject`:
     - iterator has more entries: return `NAME` (the iterator is not advanced);
     - otherwise: `END_OBJECT`.
   - Otherwise the container is a `JsonArray`:
     - iterator has more elements: advance the iterator and **push the element it returns onto the stack**, then return the token of that element (as determined by rules 3 to 6 below, i.e. as if that element had been the top all along);
     - otherwise: `END_ARRAY`.
3. The top entry is a `JsonObject`: `BEGIN_OBJECT`. A `JsonArray`: `BEGIN_ARRAY`.
4. A `JsonPrimitive`: `STRING` if it is a string, `BOOLEAN` if a boolean, `NUMBER` if a number.
5. A `JsonNull`: `NULL`.
6. The closed-reader sentinel: throw `IllegalStateException` with message `JsonReader is closed`.
7. Any other kind of entry is an internal error: throw `AssertionError`.

Repeated calls without consuming anything return the same token (after an array element was pushed by the first call, the second call simply sees that element on top). The only state change `peek()` ever makes is the step into the next array element described in rule 2.

## 3. Input specification

No parameters. The result depends only on the reader state: element trees may be arbitrarily large and deeply nested; arrays may be empty; objects may be empty.

## 4. Output specification

Returns a `JsonToken`. Examples:

- reader over `{}` fresh: `BEGIN_OBJECT`; after `beginObject()`: `END_OBJECT`; after `endObject()`: `END_DOCUMENT`.
- reader over `[1,"a",null]` after `beginArray()`: `NUMBER`; after `nextString()`: `STRING`; then `NULL`; then `END_ARRAY`.
- reader over `{"a":1}` after `beginObject()`: `NAME`; after `nextName()`: `NUMBER`.
- after `skipValue()` of the only value in a document: `END_DOCUMENT`.
- after `close()`: `IllegalStateException("JsonReader is closed")`.

## 5. Edge cases and constraints

- A fresh reader over a `JsonPrimitive` returns `STRING` / `NUMBER` / `BOOLEAN` for that value; over `JsonNull` returns `NULL`.
- Type classification of a `JsonPrimitive` follows its own `isString()`, `isBoolean()`, `isNumber()`.
- Constant time per call (apart from the push); not thread-safe.
