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

`StringsComparator.buildScript(start1, end1, start2, end2, script)` appends to `script` the shortest sequence of keep, delete and insert commands that transforms `left[start1, end1)` into `right[start2, end2)`. It works recursively by splitting the problem at the middle snake of a shortest edit path (Myers' linear-space diff).

## 2. Functional requirements

1. Compute the middle snake of the two ranges with the helper `getMiddleSnake(start1, end1, start2, end2)` (see context; it may be `null`).
2. **Base case.** If the middle snake is `null`, or if it starts at the very end of the first range on the diagonal that leads to the end of the second range (its start index equals `end1` and its diagonal number equals the difference `end1` minus `end2`), or it ends at the beginning of the first range on the diagonal of the beginning (its end index equals `start1` and its diagonal number equals `start1` minus `start2`), then no split is useful and the ranges are handled directly, scanning from the beginning with positions `i = start1` and `j = start2` until both ranges are consumed:
   - if both ranges still have characters and the character of `left` at `i` equals the character of `right` at `j`, append a `KeepCommand` with that character and advance both;
   - otherwise, if the first range is longer than the second (`end1 - start1 > end2 - start2`, measured on the original ranges, not what is left), append a `DeleteCommand` with `left.charAt(i)` and advance `i`;
   - otherwise append an `InsertCommand` with `right.charAt(j)` and advance `j`.
3. **Recursive case.** Otherwise:
   - first handle the part before the snake: the same procedure on the ranges from `start1` to the snake's start index (first sequence) and from `start2` to the snake's start index minus its diagonal number (second sequence);
   - then append a `KeepCommand` for every character `left.charAt(i)` with `snake.getStart() <= i < snake.getEnd()`;
   - then handle the part after it: the same procedure on the ranges from the snake's end index to `end1` (first sequence) and from the snake's end index minus its diagonal number to `end2` (second sequence).
4. Commands are appended in order from the beginning of the sequences to their end.

## 3. Input specification

`0 <= start1 <= end1 <= left.length()`, `0 <= start2 <= end2 <= right.length()`; `script` a non-null `EditScript<Character>` (it may already contain commands, new ones are appended after them).

## 4. Output specification

No return value; `script` is extended. Keep and delete commands carry characters of `left`, insert commands characters of `right`. The number of delete plus insert commands appended is the minimum possible, and replaying the commands on `left[start1,end1)` gives `right[start2,end2)`. Examples (full ranges): `left = "abc"`, `right = "abc"` gives three keep commands (`a`, `b`, `c`); `left = ""`, `right = "ab"` gives insert `a`, insert `b`; `left = "ab"`, `right = ""` gives delete `a`, delete `b`.

## 5. Edge cases and constraints

- The exact choice among equally short scripts (order of delete and insert commands, which equal characters are kept) is fixed by the rules above and is observable.
- Both ranges empty: nothing is appended. One range empty: all remaining characters of the other are appended as inserts or deletes.
- Neither `left` nor `right` is modified; the scratch state of the comparator may be overwritten.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/diff/StringsComparator.java`
- **Enclosing scope:** `public class StringsComparator`

## Imports / includes available in this file

```
(none)
```

## Other functions defined in the same file (signatures only; you may call them)

```
StringsComparator::Snake::Snake( final int start , final int end , final int diag)
StringsComparator::Snake::getDiag()
StringsComparator::Snake::getEnd()
StringsComparator::Snake::getStart()
StringsComparator::StringsComparator( final String left , final String right)
StringsComparator::buildSnake( final int start , final int diag , final int end1 , final int end2)
StringsComparator::getMiddleSnake( final int start1 , final int end1 , final int start2 , final int end2)
StringsComparator::getScript()
```

## Instance state

Fields of `StringsComparator` (all `private final`):

- `left` (`String`): the first sequence. `right` (`String`): the second sequence.
- `vDown` (`int[]`) and `vUp` (`int[]`): scratch arrays, each of length `left.length() + right.length() + 2`, freshly allocated (zero filled) by the constructor. They hold furthest-reaching x coordinates (indices into `left`) of the forward and the reverse search paths per diagonal, and may be freely overwritten by the method.

Nested class `private static class Snake` with constructor `Snake(int start, int end, int diag)` and getters `getStart()`, `getEnd()`, `getDiag()`: a run of matching characters, `start`/`end` are indices into `left` (half open), and `diag = x - y` where `x` indexes `left` and `y` indexes `right`, so the matching characters are `left.charAt(i) == right.charAt(i - diag)` for `start <= i < end`.

Helper `private Snake buildSnake(int start, int diag, int end1, int end2)`: returns the snake starting at `start` on diagonal `diag`, extended forward while `end < end1`, `end - diag < end2` and `left.charAt(end) == right.charAt(end - diag)`.


`getMiddleSnake(int start1, int end1, int start2, int end2)` (private, returns `Snake`, or `null` if either range is empty) finds the middle snake of a shortest edit path between `left[start1, end1)` and `right[start2, end2)`. `EditScript<Character>` (package `org.apache.commons.text.diff`) has `append(KeepCommand<Character>)`, `append(InsertCommand<Character>)`, `append(DeleteCommand<Character>)`; the command classes `KeepCommand<T>(T)`, `InsertCommand<T>(T)`, `DeleteCommand<T>(T)` have public one-argument constructors.

=== STUB ===
```java
private void buildScript(final int start1, final int end1, final int start2, final int end2,
        final EditScript<Character> script) {
    // TODO: implement according to the specification
}
```
