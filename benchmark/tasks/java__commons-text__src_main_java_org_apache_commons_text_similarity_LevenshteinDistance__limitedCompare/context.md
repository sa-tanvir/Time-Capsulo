# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/similarity/LevenshteinDistance.java`
- **Enclosing scope:** `public class LevenshteinDistance implements EditDistance<Integer>`

## Imports / includes available in this file

```
import java.util.Arrays;
```

## Other functions defined in the same file (signatures only; you may call them)

```
LevenshteinDistance::LevenshteinDistance( final Integer threshold)
LevenshteinDistance::LevenshteinDistance()
LevenshteinDistance::apply( final CharSequence left , final CharSequence right)
LevenshteinDistance::getDefaultInstance()
LevenshteinDistance::getThreshold()
LevenshteinDistance::unlimitedCompare( CharSequence left , CharSequence right)
```

## Instance state

`limitedCompare` is a private static method and reads no fields. It is called from the instance method `apply(CharSequence, CharSequence)` when the instance was built with a non-null threshold (the `Integer threshold` field, passed here as the third parameter). `unlimitedCompare(CharSequence, CharSequence)` is the sibling used when no threshold is set.
