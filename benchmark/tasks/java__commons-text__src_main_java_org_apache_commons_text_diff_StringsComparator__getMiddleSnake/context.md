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
StringsComparator::buildScript( final int start1 , final int end1 , final int start2 , final int end2 , final EditScript<Character> script)
StringsComparator::buildSnake( final int start , final int diag , final int end1 , final int end2)
StringsComparator::getScript()
```

## Instance state

Fields of `StringsComparator` (all `private final`):

- `left` (`String`): the first sequence. `right` (`String`): the second sequence.
- `vDown` (`int[]`) and `vUp` (`int[]`): scratch arrays, each of length `left.length() + right.length() + 2`, freshly allocated (zero filled) by the constructor. They hold furthest-reaching x coordinates (indices into `left`) of the forward and the reverse search paths per diagonal, and may be freely overwritten by the method.

Nested class `private static class Snake` with constructor `Snake(int start, int end, int diag)` and getters `getStart()`, `getEnd()`, `getDiag()`: a run of matching characters, `start`/`end` are indices into `left` (half open), and `diag = x - y` where `x` indexes `left` and `y` indexes `right`, so the matching characters are `left.charAt(i) == right.charAt(i - diag)` for `start <= i < end`.

Helper `private Snake buildSnake(int start, int diag, int end1, int end2)`: returns the snake starting at `start` on diagonal `diag`, extended forward while `end < end1`, `end - diag < end2` and `left.charAt(end) == right.charAt(end - diag)`.

