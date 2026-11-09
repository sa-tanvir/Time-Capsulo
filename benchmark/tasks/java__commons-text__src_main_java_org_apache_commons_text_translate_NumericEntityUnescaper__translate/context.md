# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/translate/NumericEntityUnescaper.java`
- **Enclosing scope:** `public enum OPTION { semiColonRequired, semiColonOptional, errorIfNoSemiColon }`

## Imports / includes available in this file

```
import java.io.IOException;
import java.io.Writer;
import java.util.Arrays;
import java.util.EnumSet;
```

## Other functions defined in the same file (signatures only; you may call them)

```
NumericEntityUnescaper::NumericEntityUnescaper( final OPTION ... options)
NumericEntityUnescaper::isSet( final OPTION option)
```

## Instance state

- `options` (`private final EnumSet<OPTION>`): the options chosen at construction. The constructor `NumericEntityUnescaper(OPTION... options)` stores the given options, or `{semiColonRequired}` if none were given.
- `OPTION` is the public nested enum with the constants `semiColonRequired`, `semiColonOptional`, `errorIfNoSemiColon`.
- `isSet(OPTION option)` returns whether `option` is in `options`.

`translate(CharSequence input, int index, Writer out)` is the abstract method of the parent class `CharSequenceTranslator`: it examines `input` at `index`, may write a replacement to `out`, and returns the number of `char`s of `input` consumed (0 if nothing was translated, in which case nothing may be written).
