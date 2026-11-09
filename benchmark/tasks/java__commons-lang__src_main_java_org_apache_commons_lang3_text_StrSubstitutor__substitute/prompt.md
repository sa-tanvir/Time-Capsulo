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

`StrSubstitutor.substitute(buf, offset, length, priorVariables)` is the core of the variable substitution engine. It edits the region `[offset, offset+length)` of a `StrBuilder` **in place**: every variable reference of the form `<prefix>name<suffix>` is replaced by its value (recursively substituted), and escaped prefixes are unescaped. Prefix, suffix, escape character, default-value delimiter and the options are taken from the substitutor instance (see the instance state in `context.md`).

## 2. Functional requirements

Let *top-level call* mean `priorVariables == null`. Scan the region from `offset` towards the end of the region (the end moves when the text is edited). At each position `pos`, ask the prefix matcher for the length of a prefix match at `pos` (matching is limited to the region). No match: advance by one character.

1. **Escapes.** If a prefix matches at `pos`, `pos > offset`, and the character just before `pos` equals the escape character:
   - if `preserveEscapes` is set: leave everything unchanged and advance `pos` by one;
   - otherwise delete the escape character from `buf` (the region and the text shift left by one, the region length shrinks by one, the call counts as having altered the text). `pos` is not changed, so scanning resumes at the character that is now one position after the start of the literal prefix; that is, the first character of the prefix is not examined again but the rest is (a prefix that overlaps itself may therefore still match starting at its second character).
2. **Variable end.** Otherwise a variable starts at `pos`. Set the cursor just after the prefix and look for the end: if `enableSubstitutionInVariables` is set and the prefix matches at the cursor, increment a nesting counter and skip the prefix; else if the suffix matches at the cursor: when the nesting counter is 0 the variable ends here, otherwise decrement the counter and skip the suffix; otherwise advance one character. If the end of the region is reached with no variable end, nothing is substituted for that prefix and scanning of the region ends (the text is left as is).
3. **Name.** The text between prefix and suffix is the name expression. If `enableSubstitutionInVariables` is set, the name expression is first itself substituted (using a separate `StrBuilder` and a top-level call: the public `substitute(StrBuilder, int, int)` can be used), and the result is the name expression. The scan position moves past the suffix.
4. **Default value.** If a value-delimiter matcher is configured (it may be `null`, meaning no defaults), scan the name expression from its first character: if `enableSubstitutionInVariables` is **not** set and a prefix matches at this index of the name expression, stop scanning (no default); if the delimiter matches at this index, the variable name is the part before the delimiter and the default value is the part after it; stop scanning. Otherwise the variable name is the whole name expression and there is no default.
5. **Cycle check.** Maintain the list `priorVariables`. If it is `null` when the first variable of a top-level call is processed, create it with one first element: the text of the `length` characters of `buf` starting at `offset` as they are at that moment. If the variable name is already contained in the list, throw `IllegalStateException` with the message `Infinite loop in property interpolation of <first element>: <names joined by "->">`, where the first element is removed from the list and the remaining names (excluding it, in order) follow. Otherwise append the variable name.
6. **Value.** Obtain the value with `resolveVariable(name, buf, startPos, endPos)` (`startPos` is the start of the prefix, `endPos` is the index just after the suffix). If it is `null`, use the default value (which may be `null`). If a value is available: replace `[startPos, endPos)` in `buf` by the value (counts as altered), then recursively process just the inserted text with the same method and the same `priorVariables` (`offset = startPos`, `length = value length`); the recursive call returns the net change in length of that region (rule 8). Adjust the scan position (`pos` ends up just after the fully expanded text), the region end and the accumulated length change by the total change (`recursive change + value length - (endPos - startPos)`). If no value is available the text of the variable is left as is and scanning continues after its suffix.
7. After the variable is handled (with or without a value), remove the last element of `priorVariables` (the variable name appended in rule 5) and continue scanning.
8. **Return value.** For a top-level call return `1` if the text was altered (any escape removal or any replacement) and `0` otherwise. For a call with a non-null `priorVariables` return the net change of the region length (the sum of the escape deletions (-1 each) and the replacements).

## 3. Input specification

`buf`: a `StrBuilder`; `offset` and `length` describe a valid region of it (`0 <= offset`, `offset + length <= buf.length()`). `priorVariables`: `null` or a list of strings (names being expanded). The instance supplies: the prefix and suffix matchers (non-null), the escape character, the optional value delimiter matcher, `enableSubstitutionInVariables`, `preserveEscapes` and the variable resolver (via `resolveVariable`).

## 4. Output specification

An `int` as in rule 8, plus the in-place modification of `buf`. Examples with the default configuration (prefix `${`, suffix `}`, escape `$`, delimiter `:-`) and a map `animal=fox`, `target=dog`, `a=A`:
- `"The ${animal} jumps over the ${target}."` -> buffer `"The fox jumps over the dog."`, returns `1`.
- `"no variables"` -> unchanged, returns `0`.
- `"$${animal}"` -> `"${animal}"`, returns `1` (with `preserveEscapes`: unchanged, returns `0`).
- `"${unknown:-fallback}"` -> `"fallback"`; `"${unknown}"` -> unchanged, returns `0`.
- `"${animal"` (no suffix) -> unchanged; `"${}"` -> unchanged.
- with `enableSubstitutionInVariables` and `key=animal`: `"${${key}}"` -> `"fox"`.
- values containing further references are expanded: `greet="Hello ${name}!"`, `name=Bob`: `"${greet}"` -> `"Hello Bob!"`.
- cyclic references (`x=${y}`, `y=${x}`) -> `IllegalStateException`.

## 5. Edge cases and constraints

- `buf` is modified in place and may reallocate its internal array during the call, so read the content afresh after edits.
- Text outside `[offset, offset+length)` must not be examined or changed (other than shifting).
- The method must run in time roughly proportional to the amount of text plus the number of replacements times the cost of editing the buffer.
- The exception type and the message format above are tested/checked.

=== CONTEXT ===
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

=== STUB ===
```java
private int substitute(final StrBuilder buf, final int offset, final int length, List<String> priorVariables) {
    // TODO: implement according to the specification
}
```
