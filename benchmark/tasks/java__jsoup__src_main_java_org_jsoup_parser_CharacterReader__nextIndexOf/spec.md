# Functional specification

## 1. Component overview

`CharacterReader.nextIndexOf(seq)` reports how far ahead of the current read position the next occurrence of a character sequence lies, without consuming anything.

## 2. Functional requirements

The reader holds an internal window (buffer) of the input: positions `bufPos` (the current read position) up to `bufLength` (exclusive) are the characters currently available. Input shorter than the buffer capacity (32768 characters, which includes all inputs in this task) lives entirely in the buffer.

1. First make sure the buffer is current by calling the reader's buffer-refill routine `bufferUp()` (it may reload the window when the read position has advanced past the refill threshold; for short inputs it changes nothing).
2. Search the buffered characters from `bufPos` for the first occurrence of `seq` (exact, case-sensitive character match, `seq` taken as `char` units; no surrogate-pair handling). The occurrence must lie completely inside the buffer, i.e. end at or before `bufLength`.
3. Return the offset of the first character of the first such occurrence relative to the current position (`index - bufPos`, so `0` means the sequence starts at the current position). Return `-1` if there is none, including when `seq` is longer than the remaining buffered text.
4. Overlapping or partial earlier matches must not hide a later full match (e.g. `aab` is found at offset 2 in `aaaab`).
5. The reader's position and state are not changed by the search.

## 3. Input specification

`seq`: a non-empty `CharSequence` (the first character is read unconditionally, so an empty sequence is outside the contract). The reader was created from a string of up to a few tens of thousands of characters (no NUL characters), and may already have been advanced by calling `advance()`.

## 4. Output specification

An `int`, `-1` or `>= 0`. Examples with the reader over `abcabcabc`:
- position 0, `abc` returns 0; after one `advance()`, `abc` returns 2; after two advances, `cab` returns 0.
- position 0, `c` returns 2; position 0, `z` returns -1; `abcabcabcd` returns -1.
- after three advances, `c` returns 2.

## 5. Edge cases and constraints

- Hot method of the tokeniser: it must not allocate and should be roughly linear in the remaining text.
- Single-character sequences are valid and behave like a character search.
