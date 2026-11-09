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

`StringUtil.appendNormalisedWhitespace(accum, string, stripLeading)` appends a whitespace-normalised copy of `string` to the `StringBuilder` `accum`, the way jsoup normalises text for `Element.text()`: runs of whitespace collapse to a single space and invisible formatting characters are dropped.

## 2. Functional requirements

Process `string` code point by code point (a surrogate pair is one code point). Existing content of `accum` is left untouched; output is only appended.

1. **Whitespace code points** are exactly: space, tab (`\t`), line feed, form feed, carriage return, and U+00A0 (non-breaking space). (`StringUtil.isActuallyWhitespace(int)` tests this.) A maximal run of whitespace code points produces a single `' '` (U+0020) in the output, regardless of which whitespace characters it contains.
2. **Invisible code points** are U+200B, U+200C, U+200D (zero-width space, non-joiner, joiner) and U+00AD (soft hyphen). (`StringUtil.isInvisibleChar(int)` tests this.) They are never appended. They are transparent to the whitespace logic: they neither end a whitespace run nor count as visible content. So `"a ​ b"` yields `"a b"`.
3. **Every other code point** is appended unchanged (including supplementary code points, and characters such as U+2003 or vertical tab that are not in the whitespace set above). Appending one ends the current whitespace run and marks that visible content has been seen.
4. **`stripLeading`**: if true, whitespace that occurs before the first visible (appended, non-whitespace) code point is dropped entirely. If false, leading whitespace becomes a single space. Trailing whitespace is never stripped: it becomes a single trailing space.
5. The run collapsing is measured on the output, not the input: whitespace separated only by invisible code points counts as one run.

## 3. Input specification

`accum`: a non-null `StringBuilder` (may already hold text). `string`: a non-null `String` of any length, possibly empty, containing any Unicode text. `stripLeading`: a boolean.

## 4. Output specification

Returns nothing (`void`); the result is appended to `accum`. Examples (appended text):
- `("  a \t b  ", false)` appends `" a b "`; with `stripLeading = true` it appends `"a b "`.
- `("  x", true)` appends `"x"`; with `false` appends `" x"`.
- `("a​b", *)` appends `"ab"`.
- `("x  y", *)` appends `"x y"`.
- `("​  ‍ a", true)` appends `"a"`.
- `("", *)` or a string of only invisible characters appends nothing.

## 5. Edge cases and constraints

- Surrogate pairs must be kept intact (do not split them).
- No locale or time dependence; the function does not modify `string` and is not thread-safe with respect to `accum`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/internal/StringUtil.java`
- **Enclosing scope:** `public final class StringUtil`

## Imports / includes available in this file

```
import org.jsoup.helper.Validate;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Arrays;
import java.util.Collection;
import java.util.Iterator;
import java.util.Stack;
```

## Other functions defined in the same file (signatures only; you may call them)

```
StringUtil::borrowBuilder()
StringUtil::in( final String needle , final String ... haystack)
StringUtil::inSorted( String needle , String [ ] haystack)
StringUtil::isActuallyWhitespace( int c)
StringUtil::isBlank( String string)
StringUtil::isInvisibleChar( int c)
StringUtil::isNumeric( String string)
StringUtil::isWhitespace( int c)
StringUtil::join( Collection strings , String sep)
StringUtil::join( Iterator strings , String sep)
StringUtil::join( String [ ] strings , String sep)
StringUtil::normaliseWhitespace( String string)
StringUtil::padding( int width)
StringUtil::releaseBuilder( StringBuilder sb)
StringUtil::resolve( URL base , String relUrl)
StringUtil::resolve( final String baseUrl , final String relUrl)
```

## Constants and helpers read by the method

- `StringUtil.isActuallyWhitespace(int c)` (public static): true for space, `\t`, `\n`, `\f`, `\r` and 160 (U+00A0).
- `StringUtil.isInvisibleChar(int c)` (public static): true for U+200B, U+200C, U+200D and U+00AD.
- `StringUtil.isWhitespace(int c)` (public static): true for space, `\t`, `\n`, `\f`, `\r` only.

=== STUB ===
```java
public static void appendNormalisedWhitespace(StringBuilder accum, String string, boolean stripLeading) {
    // TODO: implement according to the specification
}
```
