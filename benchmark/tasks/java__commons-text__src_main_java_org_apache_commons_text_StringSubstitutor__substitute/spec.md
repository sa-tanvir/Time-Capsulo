# Functional specification

## 1. Component overview

`StringSubstitutor.substitute(buf, offset, length, priorVariables)` is the core of variable substitution. It replaces variable references such as `${name}` or `${name:-default}` inside the region `[offset, offset + length)` of a `TextStringBuilder`, in place. It handles escaped references, nested references (in variable names and in resolved values), default values, undefined variables and cyclic definitions.

## 2. Functional requirements

Let `prefix`, `suffix`, `escape` and `delimiter` be the configured matchers/characters (see the instance state). The region is scanned left to right with a position `pos` starting at `offset`; the end of the region moves as the buffer changes.

1. **Finding a reference.** At each position check whether the prefix matches (matching never looks outside the region). If not, move on by one character.
2. **Escapes.** If the prefix matches at a position `> offset` and the character just before it equals `escape`: if `preserveEscapes` is true, leave the text unchanged and move on by one character; otherwise delete the escape character from the buffer (the region becomes one character shorter) and the reference is **not** substituted (its text stays literally in the output, without the escape). A prefix at `offset` itself is never treated as escaped.
3. **Finding the end.** Otherwise the reference starts here. After the prefix, scan for the suffix. If `enableSubstitutionInVariables` is true, each further occurrence of the prefix inside the reference opens a nested level and a suffix closes the innermost open level first; the reference ends at the suffix that closes level zero. If `enableSubstitutionInVariables` is false, the first suffix ends the reference. If the region ends before a closing suffix is found, nothing is substituted for this reference and the scan ends (the rest of the region is left as it is).
4. **Name and default.** The text between prefix and suffix is the name expression. If `enableSubstitutionInVariables`, first perform a complete top-level substitution on that expression (as a separate builder) and use the result. If a value delimiter is configured, the expression is split at the **first** delimiter occurrence into the variable name (before) and a default value (after); but if `enableSubstitutionInVariables` is false, the search for the delimiter stops (no default) at the first position where the prefix matches inside the expression. Without a delimiter match the whole expression is the name and there is no default.
5. **Cycle detection.** Keep a list of the variable names being resolved (`priorVariables`). If the list is `null` (outermost call) create it, with the text of the region (as it is when the first reference is resolved) as its first element. Before resolving a name call `checkCyclicSubstitution(name, list)`, which throws `IllegalStateException` with the message `Infinite loop in property interpolation of <first element>: <remaining names joined by "->">` if the name is already in the list; then add the name to the list.
6. **Resolving.** The value is `resolveVariable(name, buf, startOfReference, endOfReference)`; if that is `null`, the default value (possibly still `null`).
   - If a value was obtained: replace the whole reference (from prefix start to suffix end) in the buffer by the value. Unless `disableSubstitutionInValues` is true, the inserted value is then itself substituted (recursively, with the same `priorVariables` list, over exactly the inserted characters). Scanning continues after the inserted (and recursively expanded) text; it is not scanned again by the outer loop.
   - If no value was obtained and `enableUndefinedVariableException` is true, throw `IllegalArgumentException` with the message `Cannot resolve variable '<name>' (enableSubstitutionInVariables=<true|false>).`
   - If no value was obtained and no exception is enabled, the reference text is left in place and scanning continues after it.
   - After handling a reference, remove the name from `priorVariables` again.
7. **Result.** Track whether anything in the buffer changed (an escape removed or a reference replaced) and the net change in the number of characters of the region. If this call was the outermost one (`priorVariables == null` on entry) return `1` if something changed, else `0`. Otherwise return the net change in length of the region (positive, negative or zero).

## 3. Input specification

`buf`: non-null builder; `offset >= 0`, `length >= 0`, `offset + length <= buf.length()`; `priorVariables`: `null` or a mutable list of names (internal use). Text outside the region is never modified.

## 4. Output specification

An `int` as in rule 7; the builder is modified in place. Examples (default settings, map `a`->`1`, `b`->`${a}x`): `${a}` becomes `1` (returns 1); `${b}` becomes `1x`; `$${a}` becomes `${a}` (escape removed); `${z:-d}` becomes `d`; `${z}` is unchanged and returns 0; `x${a` is unchanged (no suffix); `${a}${a}` becomes `11`; a variable whose value refers back to itself (`c` -> `${c}`) throws `IllegalStateException` with `Infinite loop in property interpolation of ${c}: c`.

## 5. Edge cases and constraints

- An empty variable name (`${}`) is looked up as the empty name.
- A buffer reallocation during replacement must not corrupt the scan.
- Exceptions leave the buffer partially modified; callers do not rely on it.
- Not thread-safe with respect to the shared builder; the substitutor's configuration is only read.
