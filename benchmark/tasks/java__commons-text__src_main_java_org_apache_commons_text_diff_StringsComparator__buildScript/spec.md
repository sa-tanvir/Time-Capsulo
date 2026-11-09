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
