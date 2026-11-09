# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/WordUtils.java`
- **Enclosing scope:** `public class WordUtils`

## Imports / includes available in this file

```
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.Validate;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
```

## Other functions defined in the same file (signatures only; you may call them)

```
WordUtils::WordUtils()
WordUtils::abbreviate( final String str , int lower , int upper , final String appendToEnd)
WordUtils::capitalize( final String str , final char ... delimiters)
WordUtils::capitalize( final String str)
WordUtils::capitalizeFully( String str , final char ... delimiters)
WordUtils::capitalizeFully( final String str)
WordUtils::containsAllWords( final CharSequence word , final CharSequence ... words)
WordUtils::generateDelimiterSet( final char [ ] delimiters)
WordUtils::initials( final String str , final char ... delimiters)
WordUtils::initials( final String str)
WordUtils::isDelimiter( final char ch , final char [ ] delimiters)
WordUtils::isDelimiter( final int codePoint , final char [ ] delimiters)
WordUtils::swapCase( final String str)
WordUtils::uncapitalize( final String str , final char ... delimiters)
WordUtils::uncapitalize( final String str)
WordUtils::wrap( final String str , final int wrapLength , final String newLineStr , final boolean wrapLongWords)
WordUtils::wrap( final String str , final int wrapLength)
```

## Instance state

`wrap` is a public static method and reads no instance state or constants. It may use `org.apache.commons.lang3.StringUtils.isBlank(CharSequence)`, `java.util.regex.Pattern` / `Matcher`, and `System.lineSeparator()`.
