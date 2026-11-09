# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/text/WordUtils.java`
- **Enclosing scope:** `public class WordUtils`

## Imports / includes available in this file

```
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
```

## Other functions defined in the same file (signatures only; you may call them)

```
WordUtils::WordUtils()
WordUtils::capitalize( final String str , final char ... delimiters)
WordUtils::capitalize( final String str)
WordUtils::capitalizeFully( String str , final char ... delimiters)
WordUtils::capitalizeFully( final String str)
WordUtils::containsAllWords( final CharSequence word , final CharSequence ... words)
WordUtils::initials( final String str , final char ... delimiters)
WordUtils::initials( final String str)
WordUtils::isDelimiter( final char ch , final char [ ] delimiters)
WordUtils::swapCase( final String str)
WordUtils::uncapitalize( final String str , final char ... delimiters)
WordUtils::uncapitalize( final String str)
WordUtils::wrap( final String str , final int wrapLength , final String newLineStr , final boolean wrapLongWords)
WordUtils::wrap( final String str , final int wrapLength)
```

## Instance state

`wrap(String, int, String, boolean, String)` is a public static method of `WordUtils` (in the deprecated `org.apache.commons.lang3.text` package); it reads no fields. The shorter overloads `wrap(str, wrapLength)` and `wrap(str, wrapLength, newLineStr, wrapLongWords)` delegate to it with `wrapOn = null`. `StringUtils.isBlank(CharSequence)` is available. `java.util.regex.Pattern` and `Matcher` are imported.
