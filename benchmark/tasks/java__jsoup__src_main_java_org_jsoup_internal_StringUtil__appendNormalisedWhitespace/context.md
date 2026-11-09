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
