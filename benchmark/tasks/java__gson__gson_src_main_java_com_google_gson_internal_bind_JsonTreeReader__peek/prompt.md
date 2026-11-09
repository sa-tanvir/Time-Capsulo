You are an expert Java developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Java code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```java code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java`
- **Enclosing scope:** `public final class JsonTreeReader extends JsonReader`

## Imports / includes available in this file

```
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import java.io.IOException;
import java.io.Reader;
import java.util.Iterator;
import java.util.Map;
import java.util.Arrays;
```

## Other functions defined in the same file (signatures only; you may call them)

```
JsonTreeReader::JsonTreeReader( JsonElement element)
JsonTreeReader::Reader()
JsonTreeReader::beginArray()
JsonTreeReader::beginObject()
JsonTreeReader::close()
JsonTreeReader::endArray()
JsonTreeReader::endObject()
JsonTreeReader::expect( JsonToken expected)
JsonTreeReader::getPath()
JsonTreeReader::hasNext()
JsonTreeReader::locationString()
JsonTreeReader::nextBoolean()
JsonTreeReader::nextDouble()
JsonTreeReader::nextInt()
JsonTreeReader::nextLong()
JsonTreeReader::nextName()
JsonTreeReader::nextNull()
JsonTreeReader::nextString()
JsonTreeReader::peekStack()
JsonTreeReader::popStack()
JsonTreeReader::promoteNameToValue()
JsonTreeReader::push( Object newTop)
JsonTreeReader::skipValue()
JsonTreeReader::toString()
```

## Instance state

`JsonTreeReader` is a `JsonReader` that reads from an in-memory `JsonElement` tree instead of text. Fields:

- `stack` (`Object[]`, private): the nesting stack, `stack[0 .. stackSize)`; the top is `stack[stackSize - 1]`. Each entry is one of: a `JsonElement` (`JsonObject`, `JsonArray`, `JsonPrimitive`, `JsonNull`) that is the next value to read; a `java.util.Iterator` (over the elements of a `JsonArray`, or over the `Map.Entry<String, JsonElement>` entries of a `JsonObject`) positioned inside a container being read; or the sentinel `SENTINEL_CLOSED`. An iterator entry sits directly above the container it iterates (so `stack[stackSize - 2]` is the `JsonObject` or `JsonArray` being iterated).
- `stackSize` (`int`, private): number of entries in use. 0 means the document has been read completely.
- `SENTINEL_CLOSED` (`private static final Object`): placed alone on the stack by `close()` (`stackSize == 1`).
- `pathNames`, `pathIndices`: path bookkeeping used by `getPath()`; `peek()` does not touch them.

Sibling methods you may call: `peekStack()` (private) returns the top entry `stack[stackSize - 1]`; `push(Object newTop)` (private) pushes an entry, growing the arrays when full; `JsonPrimitive.isString()`, `isBoolean()`, `isNumber()`; `JsonToken` is `com.google.gson.stream.JsonToken`.

=== STUB ===
```java
@Override public JsonToken peek() throws IOException {
    // TODO: implement according to the specification
}
```
