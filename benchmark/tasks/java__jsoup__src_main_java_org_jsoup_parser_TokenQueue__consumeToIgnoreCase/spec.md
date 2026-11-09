# Functional specification

## 1. Component overview

`TokenQueue.consumeToIgnoreCase(seq)` consumes characters from the front of the queue up to, but not including, the next position where `seq` occurs (ignoring case), and returns the consumed text. jsoup uses it to find the end of raw-text elements such as `</script` or `</textarea`.

## 2. Functional requirements

Let the queue hold `queue` and let `pos` be the current read position (characters before `pos` have already been consumed).

1. Find the smallest position `p >= pos` such that the characters of the queue starting at `p` match `seq` case-insensitively (as `TokenQueue.matches(String)` does: `String.regionMatches` with `ignoreCase`; a match needs the full length of `seq` to be available). A match at `pos` itself counts.
2. Advance the position to `p` and return the text between the old position and `p`. If the queue is already positioned at a match, return the empty string and do not move.
3. If there is no match anywhere in the remaining text, consume everything: the position moves to the end of the queue and the whole remaining text is returned (empty if the queue was already empty).
4. The matched text itself is not consumed. A later call on the same queue starts from where this one stopped (typically after the caller has consumed the matched sequence; for example `chompToIgnoreCase` consumes `seq` afterwards, so two successive calls with the same `seq` return the text before the first and then before the second occurrence).
5. The result can be an empty string. The queue is otherwise unchanged.

## 3. Input specification

`seq`: a non-empty string (its first character is used; an empty `seq` is outside the contract). The queue holds any text, up to about 200,000 characters. Case-insensitive comparison follows `String.regionMatches(true, ...)`, with no locale dependence (so `"ss"` does not match `"ß"`).

## 4. Output specification

The consumed `String`. Examples:
- queue `<textarea>one < two </TEXTarea> third </TEXTarea>`, `seq = "</textarea>"`: returns `<textarea>one < two ` and leaves the queue positioned at `</TEXTarea> third </TEXTarea>`. After the caller removes the matched `</TEXTarea>`, a second call returns ` third `.
- queue `<textarea> one two < three </oops>`, `seq = "</textarea"`: returns the whole text; the queue is then empty.
- queue `abc`, `seq = "ABC"`: returns `""`, position unchanged.
- queue `aAbB`, `seq = "b"`: returns `aA`.

## 5. Edge cases and constraints

- Must run in time roughly linear in the consumed text and terminate for every input.
- Does not throw for any non-empty `seq`; a partial match at the very end of the queue is not a match.
