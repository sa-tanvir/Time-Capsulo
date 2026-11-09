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

`StringUtils.replaceEach(text, searchList, replacementList, repeat, timeToLive)` is the private worker behind the public `replaceEach` and `replaceEachRepeatedly`. It replaces many search strings in `text` in a single left-to-right pass, optionally repeating the whole pass until the text stops changing.

## 2. Functional requirements

1. Return `text` unchanged (the same value, which may be `null`) when `text` is `null` or empty, or when `searchList` or `replacementList` is `null` or has length 0. These checks come first, before any other check.
2. If `timeToLive < 0`, throw `IllegalStateException` with the message `Aborting to protect against StackOverflowError - output of one loop is the input of another`.
3. If both arrays are non-empty but their lengths differ, throw `IllegalArgumentException` with the message `Search and Replace array lengths don't match: <searchLength> vs <replacementLength>` (for example `1 vs 2`).
4. One pass: scan `text` from the left. At each step find, among all search strings still present at or after the current position, the one with the **smallest match index**; if several match at that same index, the one with the **lowest index in `searchList`** wins. Copy the text before the match, append the corresponding replacement, and continue scanning right after the matched search string. Replacement text is never rescanned within the same pass, and matches never overlap.
5. A search entry is ignored (never matches) if the search string is `null` or empty, or if its replacement is `null`. A replacement may be the empty string (deletes the match).
6. If no search string occurs in `text`, return `text` unchanged.
7. If `repeat` is `false`, return the result of the single pass. If `repeat` is `true`, and the pass replaced at least one match, repeat the whole procedure (rules 1 to 7) on the result with `timeToLive - 1` and the same arrays, and return that outcome. A round that finds no match returns its input. Consequently, a round that replaced something while `timeToLive` is `0` leads to the `IllegalStateException` of rule 2 (the recursive call has `timeToLive == -1`), unless the result is empty (rule 1 applies first).
8. Inputs are not modified.

## 3. Input specification

`text`: `String`, may be `null` or empty. `searchList`, `replacementList`: `String[]`, either may be `null` or empty, elements may be `null` or empty. `repeat`: `boolean`. `timeToLive`: `int` (the public callers pass `0` for the non-repeating variant and `searchList.length` for the repeating one).

## 4. Output specification

A `String` (or `null` only when `text` is `null`). Examples:
- `("aba", ["a"], [""], false, 0)` -> `"b"`
- `("abcde", ["ab","d"], ["w","t"], false, 0)` -> `"wcte"`
- `("abcde", ["ab","d"], ["d","t"], false, 0)` -> `"dcte"`
- `("abc", ["a","b"], ["b","c"], false, 0)` -> `"bcc"`
- `("abc", ["a","b"], ["b","c"], true, 2)` -> `"ccc"`
- `("abcde", ["ab","d"], ["d","t"], true, 2)` -> `"tcte"`
- `("abcde", ["ab","d"], ["d","ab"], true, 2)` -> `IllegalStateException` (the output of one round is the input of the next forever)
- `("aba", ["a","b"], ["c", null], false, 0)` -> `"cbc"`
- `("aba", [null], ["a"], false, 0)` -> `"aba"`
- `("abba", ["a"], ["b","a"], false, 0)` -> `IllegalArgumentException` (`1 vs 2`)

## 5. Edge cases and constraints

- A `null`/empty `text` returns before the `timeToLive` and length checks; a negative `timeToLive` with a non-null non-empty text and non-empty arrays throws even if nothing would match.
- Performance matters: the pass should be linear in the text length times the number of search strings, without building the result through repeated string concatenation.
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
StringUtils::splitWorker( final String str , final String separatorChars , final int max , final boolean preserveAllTokens)
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

`replaceEach(String, String[], String[], boolean, int)` is a private static method of `StringUtils`; it reads no fields or constants. It is called by the public overloads `replaceEach(text, searchList, replacementList)` (with `repeat=false`, `timeToLive=0`) and `replaceEachRepeatedly(text, searchList, replacementList)` (with `repeat=true`, `timeToLive=searchList.length`, or 0 when `searchList` is null). It may call itself recursively.

=== STUB ===
```java
private static String replaceEach(
        final String text, final String[] searchList, final String[] replacementList, final boolean repeat, final int timeToLive) {
    // TODO: implement according to the specification
}
```
