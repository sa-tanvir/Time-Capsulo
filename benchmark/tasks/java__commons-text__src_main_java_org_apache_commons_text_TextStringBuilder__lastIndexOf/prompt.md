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

`TextStringBuilder.lastIndexOf(str, startIndex)` searches the builder's content backwards for the last occurrence of `str` that starts at or before `startIndex`, and returns its start position (or `-1`). It is the `String` counterpart of `String.lastIndexOf(String, int)`, with lenient handling of bad arguments.

## 2. Functional requirements

Let `size` be the number of characters currently in the builder and `s` the content `buffer[0..size)`.

1. **Clamp the start.** If `startIndex >= size`, it is replaced by `size - 1`.
2. If `str` is `null`, or the (clamped) `startIndex` is negative, return `-1`. (This includes any search on an empty builder, because the clamped start is then `-1`, even for an empty `str`.)
3. If `str` is empty, return the (clamped) `startIndex`.
4. If `str` is longer than `size`, return `-1`.
5. If `str` has length 1, the result equals `lastIndexOf(str.charAt(0), startIndex)`.
6. Otherwise return the greatest index `i >= 0` such that the match lies entirely at or before the (clamped) `startIndex` (that is, `i + str.length() - 1 <= startIndex`) and `s[i .. i+str.length())` equals `str`. If no such `i` exists, return `-1`.

## 3. Input specification

`str`: any string or `null`. `startIndex`: any `int` (negative, in range, or beyond the size). The builder may be empty and its internal array may be larger than `size` with arbitrary leftover characters after the content.

## 4. Output specification

An `int`: the index of the last match, or `-1`. The method never throws. Examples with content `"abcabc"` (size 6): `lastIndexOf("bc", 5)` = 4; `lastIndexOf("bc", 4)` = 1 (the match at 4 would end at index 5, beyond the start); `lastIndexOf("bc", 100)` = 4; `lastIndexOf("abc", -1)` = -1; `lastIndexOf("", 3)` = 3; `lastIndexOf("", 100)` = 5; `lastIndexOf(null, 3)` = -1; `lastIndexOf("abcabcabc", 5)` = -1; `lastIndexOf("a", 5)` = 3; `lastIndexOf("x", 5)` = -1.

## 5. Edge cases and constraints

- Does not modify the builder; matches never extend beyond `size` (stale characters in the backing array must not be matched).
- Matches are case sensitive.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/TextStringBuilder.java`
- **Enclosing scope:** `public class TextStringBuilder implements CharSequence, Appendable, Serializable, Builder<String>`

## Imports / includes available in this file

```
import java.io.IOException;
import java.io.Reader;
import java.io.Serializable;
import java.io.Writer;
import java.nio.CharBuffer;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;
import org.apache.commons.text.matcher.StringMatcher;
```

## Other functions defined in the same file (signatures only; you may call them)

```
TextStringBuilder::StrBuilderReader::StrBuilderReader()
TextStringBuilder::StrBuilderReader::close()
TextStringBuilder::StrBuilderReader::mark( final int readAheadLimit)
TextStringBuilder::StrBuilderReader::markSupported()
TextStringBuilder::StrBuilderReader::read( final char [ ] b , final int off , int len)
TextStringBuilder::StrBuilderReader::read()
TextStringBuilder::StrBuilderReader::ready()
TextStringBuilder::StrBuilderReader::reset()
TextStringBuilder::StrBuilderReader::skip( long n)
TextStringBuilder::StrBuilderWriter::StrBuilderWriter()
TextStringBuilder::StrBuilderWriter::close()
TextStringBuilder::StrBuilderWriter::flush()
TextStringBuilder::StrBuilderWriter::write( final String str , final int off , final int len)
TextStringBuilder::StrBuilderWriter::write( final String str)
TextStringBuilder::StrBuilderWriter::write( final char [ ] cbuf , final int off , final int len)
TextStringBuilder::StrBuilderWriter::write( final char [ ] cbuf)
TextStringBuilder::StrBuilderWriter::write( final int c)
TextStringBuilder::TextStringBuilder( final String str)
TextStringBuilder::TextStringBuilder( int initialCapacity)
TextStringBuilder::TextStringBuilder()
TextStringBuilder::TextStringBuilderTokenizer::TextStringBuilderTokenizer()
TextStringBuilder::TextStringBuilderTokenizer::getContent()
TextStringBuilder::TextStringBuilderTokenizer::tokenize( final char [ ] chars , final int offset , final int count)
TextStringBuilder::append( final CharBuffer buf , final int startIndex , final int length)
TextStringBuilder::append( final CharBuffer buf)
TextStringBuilder::append( final CharSequence seq , final int startIndex , final int endIndex)
TextStringBuilder::append( final CharSequence seq)
TextStringBuilder::append( final Object obj)
TextStringBuilder::append( final String format , final Object ... objs)
TextStringBuilder::append( final String str , final int startIndex , final int length)
TextStringBuilder::append( final String str)
TextStringBuilder::append( final StringBuffer str , final int startIndex , final int length)
TextStringBuilder::append( final StringBuffer str)
TextStringBuilder::append( final StringBuilder str , final int startIndex , final int length)
TextStringBuilder::append( final StringBuilder str)
TextStringBuilder::append( final TextStringBuilder str , final int startIndex , final int length)
TextStringBuilder::append( final TextStringBuilder str)
TextStringBuilder::append( final boolean value)
TextStringBuilder::append( final char [ ] chars , final int startIndex , final int length)
TextStringBuilder::append( final char [ ] chars)
TextStringBuilder::append( final char ch)
TextStringBuilder::append( final double value)
TextStringBuilder::append( final float value)
TextStringBuilder::append( final int value)
TextStringBuilder::append( final long value)
TextStringBuilder::appendAll( @ SuppressWarnings("unchecked") final T ... array)
TextStringBuilder::appendAll( final Iterable <?> iterable)
TextStringBuilder::appendAll( final Iterator <?> it)
TextStringBuilder::appendFixedWidthPadLeft( final Object obj , final int width , final char padChar)
TextStringBuilder::appendFixedWidthPadLeft( final int value , final int width , final char padChar)
TextStringBuilder::appendFixedWidthPadRight( final Object obj , final int width , final char padChar)
TextStringBuilder::appendFixedWidthPadRight( final int value , final int width , final char padChar)
TextStringBuilder::appendNewLine()
TextStringBuilder::appendNull()
TextStringBuilder::appendPadding( final int length , final char padChar)
TextStringBuilder::appendSeparator( final String separator , final int loopIndex)
TextStringBuilder::appendSeparator( final String separator)
TextStringBuilder::appendSeparator( final String standard , final String defaultIfEmpty)
TextStringBuilder::appendSeparator( final char separator , final int loopIndex)
TextStringBuilder::appendSeparator( final char separator)
TextStringBuilder::appendSeparator( final char standard , final char defaultIfEmpty)
TextStringBuilder::appendTo( final Appendable appendable)
TextStringBuilder::appendWithSeparators( final Iterable <?> iterable , final String separator)
TextStringBuilder::appendWithSeparators( final Iterator <?> it , final String separator)
TextStringBuilder::appendWithSeparators( final Object [ ] array , final String separator)
TextStringBuilder::appendln( final Object obj)
TextStringBuilder::appendln( final String format , final Object ... objs)
TextStringBuilder::appendln( final String str , final int startIndex , final int length)
TextStringBuilder::appendln( final String str)
TextStringBuilder::appendln( final StringBuffer str , final int startIndex , final int length)
TextStringBuilder::appendln( final StringBuffer str)
TextStringBuilder::appendln( final StringBuilder str , final int startIndex , final int length)
TextStringBuilder::appendln( final StringBuilder str)
TextStringBuilder::appendln( final TextStringBuilder str , final int startIndex , final int length)
TextStringBuilder::appendln( final TextStringBuilder str)
TextStringBuilder::appendln( final boolean value)
TextStringBuilder::appendln( final char [ ] chars , final int startIndex , final int length)
TextStringBuilder::appendln( final char [ ] chars)
TextStringBuilder::appendln( final char ch)
TextStringBuilder::appendln( final double value)
TextStringBuilder::appendln( final float value)
TextStringBuilder::appendln( final int value)
TextStringBuilder::appendln( final long value)
TextStringBuilder::asReader()
TextStringBuilder::asTokenizer()
TextStringBuilder::asWriter()
TextStringBuilder::build()
TextStringBuilder::capacity()
TextStringBuilder::charAt( final int index)
TextStringBuilder::clear()
TextStringBuilder::contains( final String str)
TextStringBuilder::contains( final StringMatcher matcher)
TextStringBuilder::contains( final char ch)
TextStringBuilder::delete( final int startIndex , int endIndex)
TextStringBuilder::deleteAll( final String str)
TextStringBuilder::deleteAll( final StringMatcher matcher)
TextStringBuilder::deleteAll( final char ch)
TextStringBuilder::deleteCharAt( final int index)
TextStringBuilder::deleteFirst( final String str)
TextStringBuilder::deleteFirst( final StringMatcher matcher)
TextStringBuilder::deleteFirst( final char ch)
TextStringBuilder::deleteImpl( final int startIndex , final int endIndex , final int len)
TextStringBuilder::endsWith( final String str)
TextStringBuilder::ensureCapacity( final int capacity)
TextStringBuilder::equals( final Object obj)
TextStringBuilder::equals( final TextStringBuilder other)
TextStringBuilder::equalsIgnoreCase( final TextStringBuilder other)
TextStringBuilder::getChars( char [ ] destination)
TextStringBuilder::getChars( final int startIndex , final int endIndex , final char [ ] destination , final int destinationIndex)
TextStringBuilder::getNewLineText()
TextStringBuilder::getNullText()
TextStringBuilder::hashCode()
TextStringBuilder::indexOf( final String str , int startIndex)
TextStringBuilder::indexOf( final String str)
TextStringBuilder::indexOf( final StringMatcher matcher , int startIndex)
TextStringBuilder::indexOf( final StringMatcher matcher)
TextStringBuilder::indexOf( final char ch , int startIndex)
TextStringBuilder::indexOf( final char ch)
TextStringBuilder::insert( final int index , String str)
TextStringBuilder::insert( final int index , final Object obj)
TextStringBuilder::insert( final int index , final char [ ] chars , final int offset , final int length)
TextStringBuilder::insert( final int index , final char [ ] chars)
TextStringBuilder::insert( final int index , final char value)
TextStringBuilder::insert( final int index , final double value)
TextStringBuilder::insert( final int index , final float value)
TextStringBuilder::insert( final int index , final int value)
TextStringBuilder::insert( final int index , final long value)
TextStringBuilder::insert( int index , final boolean value)
TextStringBuilder::isEmpty()
TextStringBuilder::lastIndexOf( final String str)
TextStringBuilder::lastIndexOf( final StringMatcher matcher , int startIndex)
TextStringBuilder::lastIndexOf( final StringMatcher matcher)
TextStringBuilder::lastIndexOf( final char ch , int startIndex)
TextStringBuilder::lastIndexOf( final char ch)
TextStringBuilder::leftString( final int length)
TextStringBuilder::length()
TextStringBuilder::midString( int index , final int length)
TextStringBuilder::minimizeCapacity()
TextStringBuilder::readFrom( final Readable readable)
TextStringBuilder::replace( final StringMatcher matcher , final String replaceStr , final int startIndex , int endIndex , final int replaceCount)
TextStringBuilder::replace( final int startIndex , int endIndex , final String replaceStr)
TextStringBuilder::replaceAll( final String searchStr , final String replaceStr)
TextStringBuilder::replaceAll( final StringMatcher matcher , final String replaceStr)
TextStringBuilder::replaceAll( final char search , final char replace)
TextStringBuilder::replaceFirst( final String searchStr , final String replaceStr)
TextStringBuilder::replaceFirst( final StringMatcher matcher , final String replaceStr)
TextStringBuilder::replaceFirst( final char search , final char replace)
TextStringBuilder::replaceImpl( final StringMatcher matcher , final String replaceStr , final int from , int to , int replaceCount)
TextStringBuilder::replaceImpl( final int startIndex , final int endIndex , final int removeLen , final String insertStr , final int insertLen)
TextStringBuilder::reverse()
TextStringBuilder::rightString( final int length)
TextStringBuilder::setCharAt( final int index , final char ch)
TextStringBuilder::setLength( final int length)
TextStringBuilder::setNewLineText( final String newLine)
TextStringBuilder::setNullText( String nullText)
TextStringBuilder::size()
TextStringBuilder::startsWith( final String str)
TextStringBuilder::subSequence( final int startIndex , final int endIndex)
TextStringBuilder::substring( final int start)
TextStringBuilder::substring( final int startIndex , int endIndex)
TextStringBuilder::toCharArray( final int startIndex , int endIndex)
TextStringBuilder::toCharArray()
TextStringBuilder::toString()
TextStringBuilder::toStringBuffer()
TextStringBuilder::toStringBuilder()
TextStringBuilder::trim()
TextStringBuilder::validateIndex( final int index)
TextStringBuilder::validateRange( final int startIndex , int endIndex)
```

## Instance state

Fields of `TextStringBuilder` read by the method:

- `buffer` (`char[]`, `protected`/package-visible): the backing array. Only positions `0 <= i < size` hold the logical content; positions at or after `size` may contain stale characters and must be ignored.
- `size` (`int`): the number of valid characters in `buffer` (equals `length()`).

Sibling method: `public int lastIndexOf(char ch, int startIndex)` returns the last index `<= startIndex` (clamped to `size - 1`) at which `ch` occurs, or `-1` (also `-1` if the clamped start is negative). You may call it.

=== STUB ===
```java
public int lastIndexOf(final String str, int startIndex) {
    // TODO: implement according to the specification
}
```
