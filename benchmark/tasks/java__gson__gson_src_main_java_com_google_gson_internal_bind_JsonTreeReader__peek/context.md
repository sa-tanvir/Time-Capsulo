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
