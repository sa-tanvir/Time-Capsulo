# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/StringSubstitutor.java`
- **Enclosing scope:** `public class StringSubstitutor`

## Imports / includes available in this file

```
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import org.apache.commons.lang3.Validate;
import org.apache.commons.text.lookup.StringLookup;
import org.apache.commons.text.lookup.StringLookupFactory;
import org.apache.commons.text.matcher.StringMatcher;
import org.apache.commons.text.matcher.StringMatcherFactory;
```

## Other functions defined in the same file (signatures only; you may call them)

```
StringSubstitutor::StringSubstitutor( final Map<String,V> valueMap , final String prefix , final String suffix , final char escape , final String valueDelimiter)
StringSubstitutor::StringSubstitutor( final Map<String,V> valueMap , final String prefix , final String suffix , final char escape)
StringSubstitutor::StringSubstitutor( final Map<String,V> valueMap , final String prefix , final String suffix)
StringSubstitutor::StringSubstitutor( final Map<String,V> valueMap)
StringSubstitutor::StringSubstitutor( final StringLookup variableResolver , final String prefix , final String suffix , final char escape , final String valueDelimiter)
StringSubstitutor::StringSubstitutor( final StringLookup variableResolver , final String prefix , final String suffix , final char escape)
StringSubstitutor::StringSubstitutor( final StringLookup variableResolver , final StringMatcher prefixMatcher , final StringMatcher suffixMatcher , final char escape , final StringMatcher valueDelimiterMatcher)
StringSubstitutor::StringSubstitutor( final StringLookup variableResolver , final StringMatcher prefixMatcher , final StringMatcher suffixMatcher , final char escape)
StringSubstitutor::StringSubstitutor( final StringLookup variableResolver)
StringSubstitutor::StringSubstitutor()
StringSubstitutor::checkCyclicSubstitution( final String varName , final List<String> priorVariables)
StringSubstitutor::createInterpolator()
StringSubstitutor::getEscapeChar()
StringSubstitutor::getStringLookup()
StringSubstitutor::getValueDelimiterMatcher()
StringSubstitutor::getVariablePrefixMatcher()
StringSubstitutor::getVariableSuffixMatcher()
StringSubstitutor::isDisableSubstitutionInValues()
StringSubstitutor::isEnableSubstitutionInVariables()
StringSubstitutor::isEnableUndefinedVariableException()
StringSubstitutor::isPreserveEscapes()
StringSubstitutor::replace( final CharSequence source , final int offset , final int length)
StringSubstitutor::replace( final CharSequence source)
StringSubstitutor::replace( final Object source , final Map<String,V> valueMap , final String prefix , final String suffix)
StringSubstitutor::replace( final Object source , final Map<String,V> valueMap)
StringSubstitutor::replace( final Object source , final Properties valueProperties)
StringSubstitutor::replace( final Object source)
StringSubstitutor::replace( final String source , final int offset , final int length)
StringSubstitutor::replace( final String source)
StringSubstitutor::replace( final StringBuffer source , final int offset , final int length)
StringSubstitutor::replace( final StringBuffer source)
StringSubstitutor::replace( final TextStringBuilder source , final int offset , final int length)
StringSubstitutor::replace( final TextStringBuilder source)
StringSubstitutor::replace( final char [ ] source , final int offset , final int length)
StringSubstitutor::replace( final char [ ] source)
StringSubstitutor::replaceIn( final StringBuffer source , final int offset , final int length)
StringSubstitutor::replaceIn( final StringBuffer source)
StringSubstitutor::replaceIn( final StringBuilder source , final int offset , final int length)
StringSubstitutor::replaceIn( final StringBuilder source)
StringSubstitutor::replaceIn( final TextStringBuilder source , final int offset , final int length)
StringSubstitutor::replaceIn( final TextStringBuilder source)
StringSubstitutor::replaceSystemProperties( final Object source)
StringSubstitutor::resolveVariable( final String variableName , final TextStringBuilder buf , final int startPos , final int endPos)
StringSubstitutor::setDisableSubstitutionInValues( final boolean disableSubstitutionInValues)
StringSubstitutor::setEnableSubstitutionInVariables( final boolean enableSubstitutionInVariables)
StringSubstitutor::setEnableUndefinedVariableException( final boolean failOnUndefinedVariable)
StringSubstitutor::setEscapeChar( final char escapeCharacter)
StringSubstitutor::setPreserveEscapes( final boolean preserveEscapes)
StringSubstitutor::setValueDelimiter( final String valueDelimiter)
StringSubstitutor::setValueDelimiter( final char valueDelimiter)
StringSubstitutor::setValueDelimiterMatcher( final StringMatcher valueDelimiterMatcher)
StringSubstitutor::setVariablePrefix( final String prefix)
StringSubstitutor::setVariablePrefix( final char prefix)
StringSubstitutor::setVariablePrefixMatcher( final StringMatcher prefixMatcher)
StringSubstitutor::setVariableResolver( final StringLookup variableResolver)
StringSubstitutor::setVariableSuffix( final String suffix)
StringSubstitutor::setVariableSuffix( final char suffix)
StringSubstitutor::setVariableSuffixMatcher( final StringMatcher suffixMatcher)
StringSubstitutor::substitute( final TextStringBuilder buf , final int offset , final int length)
```

## Instance state

Private fields of `StringSubstitutor` (read through the public getters listed above):

- `escapeChar` (`char`): the escape character, default `'$'` (`getEscapeChar()`).
- `prefixMatcher` (`StringMatcher`): matches the variable prefix, default `"${"` (`getVariablePrefixMatcher()`).
- `suffixMatcher` (`StringMatcher`): matches the variable suffix, default `"}"` (`getVariableSuffixMatcher()`).
- `valueDelimiterMatcher` (`StringMatcher`, may be `null`): separates a variable name from its default value, default `":-"` (`getValueDelimiterMatcher()`).
- `variableResolver` (`StringLookup`): used by `resolveVariable`.
- `enableSubstitutionInVariables` (`boolean`): variable names may themselves contain variables (`isEnableSubstitutionInVariables()`).
- `preserveEscapes` (`boolean`): keep the escape character in the output (`isPreserveEscapes()`, or directly the field `preserveEscapes`).
- `disableSubstitutionInValues` (`boolean`): resolved values are not scanned again (`isDisableSubstitutionInValues()`).
- `enableUndefinedVariableException` (`boolean`): fail on unresolved variables (`isEnableUndefinedVariableException()`).

`StringMatcher.isMatch(char[] buffer, int pos, int bufferStart, int bufferEnd)` returns the number of characters matched at `pos` (0 for no match) and never looks outside `[bufferStart, bufferEnd)`.

`TextStringBuilder` (same package): `char[] buffer` (package-visible array; **re-read it after any modification**, because the builder may reallocate it; only `buffer[0..length())` is content), `length()`, `deleteCharAt(int index)`, `replace(int startIndex, int endIndex, String replaceStr)`.

Helpers of the same class: `resolveVariable(String variableName, TextStringBuilder buf, int startPos, int endPos)` returns the value or `null`; `checkCyclicSubstitution(String varName, List<String> priorVariables)` throws if `varName` is already in the list (and mutates the list while doing so); the public `substitute(TextStringBuilder buf, int offset, int length)` performs a complete top-level substitution on a region and returns whether anything changed.
