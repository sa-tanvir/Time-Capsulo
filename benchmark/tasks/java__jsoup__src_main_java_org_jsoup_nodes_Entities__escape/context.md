# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/nodes/Entities.java`
- **Enclosing scope:** `public enum EscapeMode`

## Imports / includes available in this file

```
import org.jsoup.SerializationException;
import org.jsoup.internal.StringUtil;
import org.jsoup.helper.Validate;
import org.jsoup.parser.CharacterReader;
import org.jsoup.parser.Parser;
import java.io.IOException;
import java.nio.charset.CharsetEncoder;
import java.util.Arrays;
import java.util.HashMap;
import static org.jsoup.nodes.Entities.EscapeMode.base;
import static org.jsoup.nodes.Entities.EscapeMode.extended;
```

## Other functions defined in the same file (signatures only; you may call them)

```
Entities::Entities()
Entities::EscapeMode( String file , int size)
Entities::appendEncoded( Appendable accum , EscapeMode escapeMode , int codePoint)
Entities::byName( final String name)
Entities::canEncode( final CoreCharset charset , final char c , final CharsetEncoder fallback)
Entities::codepointForName( final String name)
Entities::codepointsForName( final String name , final int [ ] codepoints)
Entities::escape( String string , Document . OutputSettings out)
Entities::escape( String string)
Entities::getByName( String name)
Entities::getCharacterByName( String name)
Entities::isBaseNamedEntity( final String name)
Entities::isNamedEntity( final String name)
Entities::load( EscapeMode e , String pointsData , int size)
Entities::nameForCodepoint( final int codepoint)
Entities::size()
Entities::unescape( String string , boolean strict)
Entities::unescape( String string)
```

## Instance state / collaborators

`escape` is a static method of the utility class `Entities` (no instance state). It reads:

- `out` (`Document.OutputSettings`): `out.escapeMode()` returns the `Entities.EscapeMode` (`xhtml`, `base` or `extended`); `out.encoder()` returns the `java.nio.charset.CharsetEncoder` for the configured charset (calling it also initialises the package-visible field `out.coreCharset`, an `Entities.CoreCharset` of `ascii`, `utf` or `fallback`, which the fast path `canEncode` below uses).
- Private static helpers in `Entities` that you may call: `appendEncoded(Appendable accum, EscapeMode escapeMode, int codePoint)` appends `&name;` using the mode's name for the code point if it has one, otherwise `&#x` + lower-case hex + `;`; `canEncode(CoreCharset charset, char c, CharsetEncoder fallback)` returns whether a BMP character can be encoded (fast paths for `ascii` and `utf`, otherwise `fallback.canEncode(c)`).
- `StringUtil.isWhitespace(int c)`: true for space, tab, line feed, form feed and carriage return.
- `Entities.EscapeMode` (enum) has the method `nameForCodepoint(int)` that gives the entity name of a code point in that mode; `escape` itself does not need to use it directly.

Constants: `Character.MIN_SUPPLEMENTARY_CODE_POINT` (0x10000). The entity tables are internal to `EscapeMode`; you do not need them.
