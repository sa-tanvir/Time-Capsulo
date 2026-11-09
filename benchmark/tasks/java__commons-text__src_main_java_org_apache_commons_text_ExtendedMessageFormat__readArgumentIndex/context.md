# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/ExtendedMessageFormat.java`
- **Enclosing scope:** `public class ExtendedMessageFormat extends MessageFormat`

## Imports / includes available in this file

```
import java.text.Format;
import java.text.MessageFormat;
import java.text.ParsePosition;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.Locale;
import java.util.Locale.Category;
import java.util.Map;
import java.util.Objects;
import org.apache.commons.text.matcher.StringMatcherFactory;
```

## Other functions defined in the same file (signatures only; you may call them)

```
ExtendedMessageFormat::ExtendedMessageFormat( final String pattern , final Locale locale , final Map<String,?extends FormatFactory> registry)
ExtendedMessageFormat::ExtendedMessageFormat( final String pattern , final Locale locale)
ExtendedMessageFormat::ExtendedMessageFormat( final String pattern , final Map<String,?extends FormatFactory> registry)
ExtendedMessageFormat::ExtendedMessageFormat( final String pattern)
ExtendedMessageFormat::appendQuotedString( final String pattern , final ParsePosition pos , final StringBuilder appendTo)
ExtendedMessageFormat::applyPattern( final String pattern)
ExtendedMessageFormat::containsElements( final Collection <?> coll)
ExtendedMessageFormat::equals( final Object obj)
ExtendedMessageFormat::getFormat( final String desc)
ExtendedMessageFormat::getQuotedString( final String pattern , final ParsePosition pos)
ExtendedMessageFormat::hashCode()
ExtendedMessageFormat::insertFormats( final String pattern , final ArrayList<String> customPatterns)
ExtendedMessageFormat::next( final ParsePosition pos)
ExtendedMessageFormat::parseFormatDescription( final String pattern , final ParsePosition pos)
ExtendedMessageFormat::seekNonWs( final String pattern , final ParsePosition pos)
ExtendedMessageFormat::setFormat( final int formatElementIndex , final Format newFormat)
ExtendedMessageFormat::setFormatByArgumentIndex( final int argumentIndex , final Format newFormat)
ExtendedMessageFormat::setFormats( final Format [ ] newFormats)
ExtendedMessageFormat::setFormatsByArgumentIndex( final Format [ ] newFormats)
ExtendedMessageFormat::toPattern()
```

## Instance state

`readArgumentIndex` is a private instance method that reads no instance fields. It uses these constants of `ExtendedMessageFormat`: `START_FMT = ','` (starts a format type), `END_FE = '}'` (ends a format element), and these helpers of the same class: `seekNonWs(String pattern, ParsePosition pos)` advances `pos` past any whitespace at its current index (stops at the end of the pattern), and `next(ParsePosition pos)` advances `pos` by one character and returns it.

`pos` (`java.text.ParsePosition`) is the cursor into `pattern`; the method reads and advances it with `getIndex()` / `setIndex(int)`.
