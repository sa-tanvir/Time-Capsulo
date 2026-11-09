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

`WordUtils.wrap(str, wrapLength, newLineStr, wrapLongWords, wrapOn)` word-wraps a string. Text is broken into lines of at most `wrapLength` characters, breaking at places matched by a regular expression (by default spaces), and lines are joined with a given line-break string.

## 2. Functional requirements

1. `str == null` -> return `null`.
2. Normalisation of the options: `newLineStr == null` -> use `System.lineSeparator()`; `wrapLength < 1` -> use `1`; `wrapOn` `null`, empty or whitespace-only -> use the single space `" "`. `wrapOn` is a Java regular expression (`Pattern`); an invalid expression throws the `PatternSyntaxException` raised by compiling it (only when `str` is not `null`).
3. Process the text from left to right, keeping a start position `offset` (initially 0), and build the result line by line. Repeat while `offset < str.length()`:
   a. Consider the *window*: the next `wrapLength + 1` characters of the text starting at `offset` (fewer near the end; the sum must not overflow for huge `wrapLength`, e.g. `Integer.MAX_VALUE`). The regular expression is applied to the window as a string of its own.
   b. If the first match in the window starts at the first character of the window, drop the matched characters (advance `offset` by the length of that first match, nothing is output) and start the next iteration (so a line never begins with a break match, e.g. leading spaces vanish; each leading match is dropped in turn).
   c. If the remaining text (from `offset` to the end) has at most `wrapLength` characters, stop: the rest is appended unchanged (including any trailing break characters).
   d. Otherwise, the break position is the start of the **last** match of the expression inside the window (all successive non-overlapping matches are examined, the last one wins; a match that starts at the last window character, i.e. at distance `wrapLength` from `offset`, counts). If there is one: append `str[offset, breakPosition)`, then `newLineStr`, and set `offset` to `breakPosition + 1` (exactly one character past the start of the match; if the match is longer, the remaining matched characters are handled by rule b in the next iteration).
   e. If the window contains no match: if `wrapLongWords` is `true`, append exactly `wrapLength` characters from `offset` followed by `newLineStr` and advance `offset` by `wrapLength` (a long word is cut). If `wrapLongWords` is `false`, look for the first match of the expression in the text **after** `offset + wrapLength`; if there is one, append `str[offset, thatMatchStart)`, then `newLineStr`, and set `offset` to `thatMatchStart + 1` (the over-long word is kept whole); if there is none, append the whole remainder and finish.
4. After the loop, append the remainder `str[offset, end)` (empty if everything has been consumed). Return the result.
5. Lines are measured in `char`s. The input is not modified.

## 3. Input specification

`str`: `String` or `null`. `wrapLength`: any `int`. `newLineStr`: any string (may be empty) or `null`. `wrapLongWords`: `boolean`. `wrapOn`: regex string or `null` (the caller avoids expressions that match the empty string).

## 4. Output specification

A `String` (or `null`). Examples (`newLineStr = "\n"` shown as `|`):
- `("Here is one line of text that is going to be wrapped after 20 columns.", 20, "|", false, null)` -> `"Here is one line of|text that is going|to be wrapped after|20 columns."`
- `("Click here to jump to the commons website - https://commons.apache.org", 20, "|", false, null)` -> `"Click here to jump|to the commons|website -|https://commons.apache.org"`
- same text with `wrapLongWords = true` -> `"Click here to jump|to the commons|website -|https://commons.apac|he.org"`
- `("flammable/inflammable", 10, "|", true, "/")` -> `"flammable|inflammabl|e"`; with length 6, `wrapLongWords = false` -> `"flammable|inflammable"`; with length 6, `true` -> `"flamma|ble|inflam|mable"`
- `("aa,,bb,,cc", 3, "|", true, ",+")` -> `"aa|bb|cc"`
- `("  leading", 20, "|", false, null)` -> `"leading"`
- `("abcdefghij", 3, "|", true, " ")` -> `"abc|def|ghi|j"`; with `wrapLongWords = false` -> `"abcdefghij"`.
- `(null, ...)` -> `null`; `("", 5, "|", true, " ")` -> `""`.

## 5. Edge cases and constraints

- Linear-ish work: the result is built incrementally; the text may be hundreds of thousands of characters long.
- Pure function, thread-safe.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/text/WordUtils.java`
- **Enclosing scope:** `public class WordUtils`

## Imports / includes available in this file

```
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
```

## Other functions defined in the same file (signatures only; you may call them)

```
WordUtils::WordUtils()
WordUtils::capitalize( final String str , final char ... delimiters)
WordUtils::capitalize( final String str)
WordUtils::capitalizeFully( String str , final char ... delimiters)
WordUtils::capitalizeFully( final String str)
WordUtils::containsAllWords( final CharSequence word , final CharSequence ... words)
WordUtils::initials( final String str , final char ... delimiters)
WordUtils::initials( final String str)
WordUtils::isDelimiter( final char ch , final char [ ] delimiters)
WordUtils::swapCase( final String str)
WordUtils::uncapitalize( final String str , final char ... delimiters)
WordUtils::uncapitalize( final String str)
WordUtils::wrap( final String str , final int wrapLength , final String newLineStr , final boolean wrapLongWords)
WordUtils::wrap( final String str , final int wrapLength)
```

## Instance state

`wrap(String, int, String, boolean, String)` is a public static method of `WordUtils` (in the deprecated `org.apache.commons.lang3.text` package); it reads no fields. The shorter overloads `wrap(str, wrapLength)` and `wrap(str, wrapLength, newLineStr, wrapLongWords)` delegate to it with `wrapOn = null`. `StringUtils.isBlank(CharSequence)` is available. `java.util.regex.Pattern` and `Matcher` are imported.

=== STUB ===
```java
public static String wrap(final String str, int wrapLength, String newLineStr, final boolean wrapLongWords, String wrapOn) {
    // TODO: implement according to the specification
}
```
