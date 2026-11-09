# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/text/StrSubstitutor.java`
- **Enclosing scope:** `public class StrSubstitutor`

## Imports / includes available in this file

```
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import org.apache.commons.lang3.StringUtils;
```

## Other functions defined in the same file (signatures only; you may call them)

```
StrSubstitutor::StrSubstitutor( final Map<String,V> valueMap , final String prefix , final String suffix , final char escape , final String valueDelimiter)
StrSubstitutor::StrSubstitutor( final Map<String,V> valueMap , final String prefix , final String suffix , final char escape)
StrSubstitutor::StrSubstitutor( final Map<String,V> valueMap , final String prefix , final String suffix)
StrSubstitutor::StrSubstitutor( final Map<String,V> valueMap)
StrSubstitutor::StrSubstitutor( final StrLookup <?> variableResolver , final StrMatcher prefixMatcher , final StrMatcher suffixMatcher , final char escape , final StrMatcher valueDelimiterMatcher)
StrSubstitutor::StrSubstitutor( final StrLookup <?> variableResolver , final StrMatcher prefixMatcher , final StrMatcher suffixMatcher , final char escape)
StrSubstitutor::StrSubstitutor( final StrLookup <?> variableResolver , final String prefix , final String suffix , final char escape , final String valueDelimiter)
StrSubstitutor::StrSubstitutor( final StrLookup <?> variableResolver , final String prefix , final String suffix , final char escape)
StrSubstitutor::StrSubstitutor( final StrLookup <?> variableResolver)
StrSubstitutor::StrSubstitutor()
StrSubstitutor::checkCyclicSubstitution( final String varName , final List<String> priorVariables)
StrSubstitutor::getEscapeChar()
StrSubstitutor::getValueDelimiterMatcher()
StrSubstitutor::getVariablePrefixMatcher()
StrSubstitutor::getVariableResolver()
StrSubstitutor::getVariableSuffixMatcher()
StrSubstitutor::isEnableSubstitutionInVariables()
StrSubstitutor::isPreserveEscapes()
StrSubstitutor::replace( final CharSequence source , final int offset , final int length)
StrSubstitutor::replace( final CharSequence source)
StrSubstitutor::replace( final Object source , final Map<String,V> valueMap , final String prefix , final String suffix)
StrSubstitutor::replace( final Object source , final Map<String,V> valueMap)
StrSubstitutor::replace( final Object source , final Properties valueProperties)
StrSubstitutor::replace( final Object source)
StrSubstitutor::replace( final StrBuilder source , final int offset , final int length)
StrSubstitutor::replace( final StrBuilder source)
StrSubstitutor::replace( final String source , final int offset , final int length)
StrSubstitutor::replace( final String source)
StrSubstitutor::replace( final StringBuffer source , final int offset , final int length)
StrSubstitutor::replace( final StringBuffer source)
StrSubstitutor::replace( final char [ ] source , final int offset , final int length)
StrSubstitutor::replace( final char [ ] source)
StrSubstitutor::replaceIn( final StrBuilder source , final int offset , final int length)
StrSubstitutor::replaceIn( final StrBuilder source)
StrSubstitutor::replaceIn( final StringBuffer source , final int offset , final int length)
StrSubstitutor::replaceIn( final StringBuffer source)
StrSubstitutor::replaceIn( final StringBuilder source , final int offset , final int length)
StrSubstitutor::replaceIn( final StringBuilder source)
StrSubstitutor::replaceSystemProperties( final Object source)
StrSubstitutor::resolveVariable( final String variableName , final StrBuilder buf , final int startPos , final int endPos)
StrSubstitutor::setEnableSubstitutionInVariables( final boolean enableSubstitutionInVariables)
StrSubstitutor::setEscapeChar( final char escapeCharacter)
StrSubstitutor::setPreserveEscapes( final boolean preserveEscapes)
StrSubstitutor::setValueDelimiter( final String valueDelimiter)
StrSubstitutor::setValueDelimiter( final char valueDelimiter)
StrSubstitutor::setValueDelimiterMatcher( final StrMatcher valueDelimiterMatcher)
StrSubstitutor::setVariablePrefix( final String prefix)
StrSubstitutor::setVariablePrefix( final char prefix)
StrSubstitutor::setVariablePrefixMatcher( final StrMatcher prefixMatcher)
StrSubstitutor::setVariableResolver( final StrLookup <?> variableResolver)
StrSubstitutor::setVariableSuffix( final String suffix)
StrSubstitutor::setVariableSuffix( final char suffix)
StrSubstitutor::setVariableSuffixMatcher( final StrMatcher suffixMatcher)
StrSubstitutor::substitute( final StrBuilder buf , final int offset , final int length)
```

## Instance state

`substitute(StrBuilder, int, int, List<String>)` is a private instance method of `StrSubstitutor`. It uses (via private fields and their getters):
- `escapeChar` (`char`, `getEscapeChar()`): escape for prefixes, default `$`.
- `prefixMatcher` / `suffixMatcher` (`StrMatcher`, `getVariablePrefixMatcher()` / `getVariableSuffixMatcher()`): non-null matchers; `matcher.isMatch(char[] buffer, int pos, int bufferStart, int bufferEnd)` returns the length of the match starting at `pos` (0 if none) without reading before `bufferStart` or at/after `bufferEnd`; `matcher.isMatch(char[] buffer, int pos)` is the same on the whole array.
- `valueDelimiterMatcher` (`StrMatcher`, may be `null`, `getValueDelimiterMatcher()`): default `:-`.
- `variableResolver` (`StrLookup<?>`) used by `resolveVariable(String name, StrBuilder buf, int startPos, int endPos)` (returns the looked-up value or `null`).
- `enableSubstitutionInVariables` (`boolean`, `isEnableSubstitutionInVariables()`) and `preserveEscapes` (`boolean`, field in the class, default `false`; `isPreserveEscapes()`).
- `checkCyclicSubstitution(String varName, List<String> priorVariables)` (private) is available and implements the cycle check of rule 5 (it throws the exception described there; otherwise it does nothing).
- Siblings: `substitute(StrBuilder buf, int offset, int length)` (returns `boolean`, calls this method with `priorVariables == null` and returns whether the result is `> 0`).
`StrBuilder` (same package) offers `length()`, `charAt`, `deleteCharAt(int)`, `replace(int startIndex, int endIndex, String replaceStr)`, `toString()`, and a package-visible field `char[] buffer` with the content in its first `length()` chars; the array object is replaced when the builder grows.
