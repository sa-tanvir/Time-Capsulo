# Functional specification

## 1. Component overview

`WordUtils.wrap(str, wrapLength, newLineStr, wrapLongWords, wrapOn)` inserts line breaks into a text so that lines are at most `wrapLength` characters long, breaking at separators given by a regular expression (by default a space). Words longer than a line are either split or left whole. The separator text at a break is replaced by the line-break string.

## 2. Functional requirements

1. If `str` is `null`, return `null`. If `newLineStr` is `null`, use `System.lineSeparator()`. If `wrapLength < 1`, use `1`. If `wrapOn` is `null`, empty or only whitespace (`StringUtils.isBlank`), use a single space `" "`. Otherwise `wrapOn` is a Java regular expression (`java.util.regex.Pattern` syntax; an invalid one throws `PatternSyntaxException`). "Separator" below means a match of this expression.
2. Processing uses a position `pos` (initially 0, an index into `str`) and an integer flag `emptyFlag` (initially `-1`). Repeat while `pos < str.length()`; the output is built by appending pieces. "Window" means the substring `str[pos, min(str.length(), pos + wrapLength + 1))`; every regex search on the window is done on that substring alone (so look-aheads cannot see past the window end, and positions are relative to the window start). Each iteration does these steps in order:
   - **(a) First match.** Find the first match in the window. Let `cand = -1`. If a match exists and starts at window offset 0: set `emptyFlag` to its length; if the length is not 0, add the length to `pos` and start the next iteration immediately (leading separator dropped); if the length is 0, add 1 to `pos` (the first character is skipped for now). Then `cand = pos + (match start)` using the *updated* `pos` (so for an empty match at offset 0, `cand` equals the new `pos`). If the first match exists and starts at window offset > 0, `cand = pos + start`. `emptyFlag` is not touched when the first match starts after offset 0.
   - **(b) Short rest.** If `str.length() - pos <= wrapLength` (with the current `pos`), leave the loop.
   - **(c) Last match.** Continue finding further matches in the same window (same matcher, so only matches after the first one); for each, set `cand = pos + (match start relative to the window start)`, using the current `pos` (after the possible +1 of step a). The last one wins. (Hence after a skipped empty match at offset 0, `cand` is one more than the true index of the match start.)
   - **(d) Normal break.** If `cand >= pos`: append `str[pos, cand)`, then `newLineStr`, and set `pos = cand + 1`.
   - **(e) Long word, `wrapLongWords == true`** (when `cand < pos`, which means no match was found): if `emptyFlag == 0`, first decrease `pos` by 1. Append `str[pos, pos + wrapLength)` and `newLineStr`, add `wrapLength` to `pos`, set `emptyFlag = -1`.
   - **(f) Long word, `wrapLongWords == false`**: search for the first match in `str[pos + wrapLength ..]` (to the end of the string, again on that substring alone). If found, set `emptyFlag` to its length and `cand = pos + wrapLength + (match start)`. If `cand >= 0`: if `emptyFlag == 0` and `pos != 0`, decrease `pos` by 1; append `str[pos, cand)` and `newLineStr`; set `pos = cand + 1`. Otherwise (no match): if `emptyFlag == 0` and `pos != 0`, decrease `pos` by 1; append `str[pos ..]` entirely, set `pos = str.length()` and `emptyFlag = -1`.
   - **After the loop:** if `emptyFlag == 0` and `pos < str.length()`, decrease `pos` by 1. Then append `str[pos ..]` (the unconsumed rest, unchanged, trailing separators included).
3. For separators that match at least one character, no characters are lost except the discarded leading separator characters and the one separator character at each break (the character at the start of the break match is replaced by the newline). 
4. Patterns that can match the empty string (for example look-aheads such as `(?=d)`) follow exactly the flag rules above (the skip of one character and the `-1` correction are intentional behaviour, not a bug to fix). These results are required exactly: `wrap("abcdef", 2, "\n", false, "(?=d)")` = `"abc\ndef"`; `wrap("abcdefabcdef", 2, "\n", false, "(?=d)")` = `"abc\ndefabc\ndef"`; `wrap("nabcdefabcdefn", 2, "\n", false, "(?=n)")` = `"\nabcdefabcdef\n"`; `wrap("abcdefggabcdef", 2, "\n", false, "(?=g)")` = `"abcdef\n\nabcdef"`; `wrap("g/cdn c/", 2, "|", false, "(?=g)")` = `"|/cdn c/"`; `wrap("gbngagdb", 1, "|", false, "(?=n)")` = `"gb|ngagdb"`; `wrap("c cnn gd -a", 3, "|", false, "(?=n)")` = `"c c|| gd -a"`.

## 3. Input specification

`str`: any string or `null`; `wrapLength`: any `int` (values below 1 are treated as 1, `Integer.MAX_VALUE` must work without overflow or exceptions); `newLineStr`: any string or `null`; `wrapLongWords`: boolean; `wrapOn`: a regular expression string, may be `null`/blank.

## 4. Output specification

The wrapped string, `""` for `""`, or `null` for `null`. Examples (`wrapOn` blank, newline `"\n"`):
- `wrap("Here is one line of text that is going to be wrapped after 20 columns.", 20, "\n", false, " ")` = `"Here is one line of\ntext that is going\nto be wrapped after\n20 columns."`
- `wrap("Here is one line", 6, "\n", false, null)` = `"Here\nis one\nline"`; with length 2: `"Here\nis\none\nline"`.
- `wrap("Click here to jump to the commons website - https://commons.apache.org", 20, "\n", false, null)` = `"Click here to jump\nto the commons\nwebsite -\nhttps://commons.apache.org"`; with `wrapLongWords = true` it is `"Click here to jump\nto the commons\nwebsite -\nhttps://commons.apac\nhe.org"`.
- `wrap("word1             word2                        word3", 7, "\n", false, null)` = `"word1  \nword2  \nword3"`.
- `wrap(" Here:  is  one  line  of  text  that  is  going  to  be  wrapped  after  20  columns.", 20, "\n", false, null)` = `"Here:  is  one  line\nof  text  that  is \ngoing  to  be \nwrapped  after  20 \ncolumns."`
- `wrap("flammable/inflammable", 30, "\n", false, "/")` = `"flammable/inflammable"`; with length 2: `"flammable\ninflammable"`; `wrap("flammable/inflammable", 9, "\n", true, "/")` = `"flammable\ninflammab\nle"`; `wrap("flammableinflammable", 15, "\n", true, "/")` = `"flammableinflam\nmable"`.

## 5. Edge cases and constraints

- Must not throw `StringIndexOutOfBoundsException` for very long words without separators or for `wrapLength = Integer.MAX_VALUE` (regression tests exist).
- The input string is not modified; the function is pure and thread-safe.
- A trailing separator at the very end of a short last line is kept.
