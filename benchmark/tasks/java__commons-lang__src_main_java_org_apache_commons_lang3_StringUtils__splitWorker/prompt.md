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

`StringUtils.splitWorker(str, separatorChars, max, preserveAllTokens)` is the private worker behind the `split(...)` and `splitPreserveAllTokens(...)` families. It splits a string into an array of tokens at any of a set of separator characters, with an optional cap on the number of tokens.

## 2. Functional requirements

1. If `str` is `null`, return `null`. If `str` is the empty string, return an empty array (for all other parameters).
2. Separators: if `separatorChars` is `null`, a separator is any character for which `Character.isWhitespace(char)` is true. Otherwise a separator is any character contained in `separatorChars`; each `char` is considered on its own, so `separatorChars` is a set of single characters, not a delimiter string. An empty `separatorChars` string contains no separators, so the whole `str` is a single token.
3. Tokens, when `preserveAllTokens` is `false`: the maximal runs of non-separator characters, in order. Adjacent separators act as one; leading and trailing separators produce nothing. A `str` made only of separators yields an empty array.
4. Tokens, when `preserveAllTokens` is `true`: every separator ends a token, so adjacent separators produce empty-string tokens between them, a separator at the very start produces a leading empty token, and a separator at the very end produces a trailing empty token. A `str` of `k` separators only yields `k + 1` empty strings. A non-empty `str` without any separator yields exactly one token (itself).
5. `max` limits the number of returned elements: `max <= 0` means no limit. If `max > 0` and the string has more than `max` tokens by the rules above, the result has exactly `max` elements, and the last element is the entire remainder of `str` starting at the beginning of the `max`-th token and running to the end of `str`, including any separators that follow (not trimmed and not split). If the number of tokens is at most `max`, nothing special happens, except that when the `max`-th token is followed by a separator, then that last element also extends to the end of the string (e.g. `"a b "`, `" "`, `2`, `false` -> `["a", "b "]`).
6. The returned array is new; `str` is not modified.

## 3. Input specification

`str`: `String` or `null`. `separatorChars`: `String` or `null` (whitespace). `max`: any `int`. `preserveAllTokens`: `boolean`.

## 4. Output specification

A `String[]` (or `null`). Examples:
- `("a b  c", null, 0, false)` -> `["a","b","c"]`
- `("a b  c", null, 0, true)` -> `["a","b","","c"]`
- `(" a ", " ", 0, true)` -> `["","a",""]`
- `(" a ", " ", 0, false)` -> `["a"]`
- `("a,b;c d", ",; ", 0, false)` -> `["a","b","c","d"]`
- `("a:b:c", ":", 2, false)` -> `["a","b:c"]`
- `("a:b:c:", ":", 3, true)` -> `["a","b","c:"]`; with max 4 -> `["a","b","c",""]`
- `("a b  c d", " ", 3, false)` -> `["a","b","c d"]`
- `("abc", "", 0, false)` -> `["abc"]`
- `("", ",", 0, true)` -> `[]`

## 5. Edge cases and constraints

- Work must be linear in the length of `str`.
- Pure function, thread-safe.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/StringUtils.java`
- **Enclosing scope:** `public class StringUtils`

## Imports / includes available in this file

```
import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.regex.Pattern;
```

## Other functions defined in the same file (signatures only; you may call them)

```
StringUtils::StringUtils()
StringUtils::abbreviate( final String str , final String abbrevMarker , final int maxWidth)
StringUtils::abbreviate( final String str , final String abbrevMarker , int offset , final int maxWidth)
StringUtils::abbreviate( final String str , final int maxWidth)
StringUtils::abbreviate( final String str , final int offset , final int maxWidth)
StringUtils::abbreviateMiddle( final String str , final String middle , final int length)
StringUtils::appendIfMissing( final String str , final CharSequence suffix , final CharSequence ... suffixes)
StringUtils::appendIfMissing( final String str , final CharSequence suffix , final boolean ignoreCase , final CharSequence ... suffixes)
StringUtils::appendIfMissingIgnoreCase( final String str , final CharSequence suffix , final CharSequence ... suffixes)
StringUtils::capitalize( final String str)
StringUtils::center( String str , final int size , String padStr)
StringUtils::center( String str , final int size , final char padChar)
StringUtils::center( final String str , final int size)
StringUtils::chomp( final String str , final String separator)
StringUtils::chomp( final String str)
StringUtils::chop( final String str)
StringUtils::compare( final String str1 , final String str2 , final boolean nullIsLess)
StringUtils::compare( final String str1 , final String str2)
StringUtils::compareIgnoreCase( final String str1 , final String str2 , final boolean nullIsLess)
StringUtils::compareIgnoreCase( final String str1 , final String str2)
StringUtils::contains( final CharSequence seq , final CharSequence searchSeq)
StringUtils::contains( final CharSequence seq , final int searchChar)
StringUtils::containsAny( final CharSequence cs , final CharSequence ... searchCharSequences)
StringUtils::containsAny( final CharSequence cs , final CharSequence searchChars)
StringUtils::containsAny( final CharSequence cs , final char ... searchChars)
StringUtils::containsIgnoreCase( final CharSequence str , final CharSequence searchStr)
StringUtils::containsNone( final CharSequence cs , final String invalidChars)
StringUtils::containsNone( final CharSequence cs , final char ... searchChars)
StringUtils::containsOnly( final CharSequence cs , final String validChars)
StringUtils::containsOnly( final CharSequence cs , final char ... valid)
StringUtils::containsWhitespace( final CharSequence seq)
StringUtils::convertRemainingAccentCharacters( final StringBuilder decomposed)
StringUtils::countMatches( final CharSequence str , final CharSequence sub)
StringUtils::countMatches( final CharSequence str , final char ch)
StringUtils::defaultIfBlank( final T str , final T defaultStr)
StringUtils::defaultIfEmpty( final T str , final T defaultStr)
StringUtils::defaultString( final String str , final String defaultStr)
StringUtils::defaultString( final String str)
StringUtils::deleteWhitespace( final String str)
StringUtils::difference( final String str1 , final String str2)
StringUtils::endsWith( final CharSequence str , final CharSequence suffix , final boolean ignoreCase)
StringUtils::endsWith( final CharSequence str , final CharSequence suffix)
StringUtils::endsWithAny( final CharSequence sequence , final CharSequence ... searchStrings)
StringUtils::endsWithIgnoreCase( final CharSequence str , final CharSequence suffix)
StringUtils::equals( final CharSequence cs1 , final CharSequence cs2)
StringUtils::equalsAny( final CharSequence string , final CharSequence ... searchStrings)
StringUtils::equalsAnyIgnoreCase( final CharSequence string , final CharSequence ... searchStrings)
StringUtils::equalsIgnoreCase( final CharSequence cs1 , final CharSequence cs2)
StringUtils::firstNonBlank( final T ... values)
StringUtils::firstNonEmpty( final T ... values)
StringUtils::getCommonPrefix( final String ... strs)
StringUtils::getDigits( final String str)
StringUtils::getFuzzyDistance( final CharSequence term , final CharSequence query , final Locale locale)
StringUtils::getJaroWinklerDistance( final CharSequence first , final CharSequence second)
StringUtils::getLevenshteinDistance( CharSequence s , CharSequence t , final int threshold)
StringUtils::getLevenshteinDistance( CharSequence s , CharSequence t)
StringUtils::indexOf( final CharSequence seq , final CharSequence searchSeq , final int startPos)
StringUtils::indexOf( final CharSequence seq , final CharSequence searchSeq)
StringUtils::indexOf( final CharSequence seq , final int searchChar , final int startPos)
StringUtils::indexOf( final CharSequence seq , final int searchChar)
StringUtils::indexOfAny( final CharSequence cs , final String searchChars)
StringUtils::indexOfAny( final CharSequence cs , final char ... searchChars)
StringUtils::indexOfAny( final CharSequence str , final CharSequence ... searchStrs)
StringUtils::indexOfAnyBut( final CharSequence cs , final char ... searchChars)
StringUtils::indexOfAnyBut( final CharSequence seq , final CharSequence searchChars)
StringUtils::indexOfDifference( final CharSequence ... css)
StringUtils::indexOfDifference( final CharSequence cs1 , final CharSequence cs2)
StringUtils::indexOfIgnoreCase( final CharSequence str , final CharSequence searchStr , int startPos)
StringUtils::indexOfIgnoreCase( final CharSequence str , final CharSequence searchStr)
StringUtils::isAllBlank( final CharSequence ... css)
StringUtils::isAllEmpty( final CharSequence ... css)
StringUtils::isAllLowerCase( final CharSequence cs)
StringUtils::isAllUpperCase( final CharSequence cs)
StringUtils::isAlpha( final CharSequence cs)
StringUtils::isAlphaSpace( final CharSequence cs)
StringUtils::isAlphanumeric( final CharSequence cs)
StringUtils::isAlphanumericSpace( final CharSequence cs)
StringUtils::isAnyBlank( final CharSequence ... css)
StringUtils::isAnyEmpty( final CharSequence ... css)
StringUtils::isAsciiPrintable( final CharSequence cs)
StringUtils::isBlank( final CharSequence cs)
StringUtils::isEmpty( final CharSequence cs)
StringUtils::isMixedCase( final CharSequence cs)
StringUtils::isNoneBlank( final CharSequence ... css)
StringUtils::isNoneEmpty( final CharSequence ... css)
StringUtils::isNotBlank( final CharSequence cs)
StringUtils::isNotEmpty( final CharSequence cs)
StringUtils::isNumeric( final CharSequence cs)
StringUtils::isNumericSpace( final CharSequence cs)
StringUtils::isWhitespace( final CharSequence cs)
StringUtils::join( final Iterable <?> iterable , final String separator)
StringUtils::join( final Iterable <?> iterable , final char separator)
StringUtils::join( final Iterator <?> iterator , final String separator)
StringUtils::join( final Iterator <?> iterator , final char separator)
StringUtils::join( final List <?> list , final String separator , final int startIndex , final int endIndex)
StringUtils::join( final List <?> list , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final Object [ ] array , String separator , final int startIndex , final int endIndex)
StringUtils::join( final Object [ ] array , final String separator)
StringUtils::join( final Object [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final Object [ ] array , final char separator)
StringUtils::join( final T ... elements)
StringUtils::join( final byte [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final byte [ ] array , final char separator)
StringUtils::join( final char [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final char [ ] array , final char separator)
StringUtils::join( final double [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final double [ ] array , final char separator)
StringUtils::join( final float [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final float [ ] array , final char separator)
StringUtils::join( final int [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final int [ ] array , final char separator)
StringUtils::join( final long [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final long [ ] array , final char separator)
StringUtils::join( final short [ ] array , final char separator , final int startIndex , final int endIndex)
StringUtils::join( final short [ ] array , final char separator)
StringUtils::joinWith( final String separator , final Object ... objects)
StringUtils::lastIndexOf( final CharSequence seq , final CharSequence searchSeq , final int startPos)
StringUtils::lastIndexOf( final CharSequence seq , final CharSequence searchSeq)
StringUtils::lastIndexOf( final CharSequence seq , final int searchChar , final int startPos)
StringUtils::lastIndexOf( final CharSequence seq , final int searchChar)
StringUtils::lastIndexOfAny( final CharSequence str , final CharSequence ... searchStrs)
StringUtils::lastIndexOfIgnoreCase( final CharSequence str , final CharSequence searchStr , int startPos)
StringUtils::lastIndexOfIgnoreCase( final CharSequence str , final CharSequence searchStr)
StringUtils::lastOrdinalIndexOf( final CharSequence str , final CharSequence searchStr , final int ordinal)
StringUtils::left( final String str , final int len)
StringUtils::leftPad( final String str , final int size , String padStr)
StringUtils::leftPad( final String str , final int size , final char padChar)
StringUtils::leftPad( final String str , final int size)
StringUtils::length( final CharSequence cs)
StringUtils::lowerCase( final String str , final Locale locale)
StringUtils::lowerCase( final String str)
StringUtils::matches( final CharSequence first , final CharSequence second)
StringUtils::mid( final String str , int pos , final int len)
StringUtils::newStringBuilder( final int noOfItems)
StringUtils::normalizeSpace( final String str)
StringUtils::ordinalIndexOf( final CharSequence str , final CharSequence searchStr , final int ordinal , final boolean lastIndex)
StringUtils::ordinalIndexOf( final CharSequence str , final CharSequence searchStr , final int ordinal)
StringUtils::overlay( final String str , String overlay , int start , int end)
StringUtils::prependIfMissing( final String str , final CharSequence prefix , final CharSequence ... prefixes)
StringUtils::prependIfMissing( final String str , final CharSequence prefix , final boolean ignoreCase , final CharSequence ... prefixes)
StringUtils::prependIfMissingIgnoreCase( final String str , final CharSequence prefix , final CharSequence ... prefixes)
StringUtils::remove( final String str , final String remove)
StringUtils::remove( final String str , final char remove)
StringUtils::removeAll( final String text , final String regex)
StringUtils::removeEnd( final String str , final String remove)
StringUtils::removeEndIgnoreCase( final String str , final String remove)
StringUtils::removeFirst( final String text , final String regex)
StringUtils::removeIgnoreCase( final String str , final String remove)
StringUtils::removePattern( final String source , final String regex)
StringUtils::removeStart( final String str , final String remove)
StringUtils::removeStartIgnoreCase( final String str , final String remove)
StringUtils::repeat( final String str , final String separator , final int repeat)
StringUtils::repeat( final String str , final int repeat)
StringUtils::repeat( final char ch , final int repeat)
StringUtils::replace( final String text , String searchString , final String replacement , int max , final boolean ignoreCase)
StringUtils::replace( final String text , final String searchString , final String replacement , final int max)
StringUtils::replace( final String text , final String searchString , final String replacement)
StringUtils::replaceAll( final String text , final String regex , final String replacement)
StringUtils::replaceChars( final String str , final String searchChars , String replaceChars)
StringUtils::replaceChars( final String str , final char searchChar , final char replaceChar)
StringUtils::replaceEach( final String text , final String [ ] searchList , final String [ ] replacementList , final boolean repeat , final int timeToLive)
StringUtils::replaceEach( final String text , final String [ ] searchList , final String [ ] replacementList)
StringUtils::replaceEachRepeatedly( final String text , final String [ ] searchList , final String [ ] replacementList)
StringUtils::replaceFirst( final String text , final String regex , final String replacement)
StringUtils::replaceIgnoreCase( final String text , final String searchString , final String replacement , final int max)
StringUtils::replaceIgnoreCase( final String text , final String searchString , final String replacement)
StringUtils::replaceOnce( final String text , final String searchString , final String replacement)
StringUtils::replaceOnceIgnoreCase( final String text , final String searchString , final String replacement)
StringUtils::replacePattern( final String source , final String regex , final String replacement)
StringUtils::reverse( final String str)
StringUtils::reverseDelimited( final String str , final char separatorChar)
StringUtils::right( final String str , final int len)
StringUtils::rightPad( final String str , final int size , String padStr)
StringUtils::rightPad( final String str , final int size , final char padChar)
StringUtils::rightPad( final String str , final int size)
StringUtils::rotate( final String str , final int shift)
StringUtils::split( final String str , final String separatorChars , final int max)
StringUtils::split( final String str , final String separatorChars)
StringUtils::split( final String str , final char separatorChar)
StringUtils::split( final String str)
StringUtils::splitByCharacterType( final String str , final boolean camelCase)
StringUtils::splitByCharacterType( final String str)
StringUtils::splitByCharacterTypeCamelCase( final String str)
StringUtils::splitByWholeSeparator( final String str , final String separator , final int max)
StringUtils::splitByWholeSeparator( final String str , final String separator)
StringUtils::splitByWholeSeparatorPreserveAllTokens( final String str , final String separator , final int max)
StringUtils::splitByWholeSeparatorPreserveAllTokens( final String str , final String separator)
StringUtils::splitByWholeSeparatorWorker( final String str , final String separator , final int max , final boolean preserveAllTokens)
StringUtils::splitPreserveAllTokens( final String str , final String separatorChars , final int max)
StringUtils::splitPreserveAllTokens( final String str , final String separatorChars)
StringUtils::splitPreserveAllTokens( final String str , final char separatorChar)
StringUtils::splitPreserveAllTokens( final String str)
StringUtils::splitWorker( final String str , final char separatorChar , final boolean preserveAllTokens)
StringUtils::startsWith( final CharSequence str , final CharSequence prefix , final boolean ignoreCase)
StringUtils::startsWith( final CharSequence str , final CharSequence prefix)
StringUtils::startsWithAny( final CharSequence sequence , final CharSequence ... searchStrings)
StringUtils::startsWithIgnoreCase( final CharSequence str , final CharSequence prefix)
StringUtils::strip( String str , final String stripChars)
StringUtils::strip( final String str)
StringUtils::stripAccents( final String input)
```

## Instance state

`splitWorker(String, String, int, boolean)` is a private static method of `StringUtils`; it reads no fields or constants. It is called by `split(str)`, `split(str, separatorChars)`, `split(str, separatorChars, max)` and the `splitPreserveAllTokens` variants (passing `max = -1` or `0` for "unlimited"). `ArrayUtils.EMPTY_STRING_ARRAY` is available for the empty result.

=== STUB ===
```java
private static String[] splitWorker(final String str, final String separatorChars, final int max, final boolean preserveAllTokens) {
    // TODO: implement according to the specification
}
```
