# Functional specification

## 1. Component overview

`DoubleMetaphone.doubleMetaphone(String value, boolean alternate)` computes the Double Metaphone phonetic key of a word or name (Lawrence Philips' algorithm, as implemented by Apache Commons Codec). Every word has a primary key and possibly a different alternate key (a second plausible pronunciation). The method returns one of them, selected by `alternate`. The key is an upper-case string of consonant codes such as `K`, `S`, `X`, `0` (the "th" sound), `J`, `F`, `P`, `N`, `M`, `L`, `R`, `T`, `A`.

The class also provides per-letter rule handling that the character-by-character scan is expected to use: `handleAEIOUY`, `handleC`, `handleD`, `handleG`, `handleH`, `handleJ`, `handleL`, `handleP`, `handleR`, `handleS`, `handleT`, `handleW`, `handleX`, `handleZ`, `conditionM0`, `isSlavoGermanic`, `isSilentStart`, `cleanInput` and a result accumulator `DoubleMetaphoneResult` (see context). You may call them. Their behaviour must not be re-implemented differently; this method decides which one is applied at each position and how far to advance.

## 2. Functional requirements

1. Normalise the input (leading and trailing whitespace removed, converted to upper case with `Locale.ENGLISH`). If the input is `null`, or is empty after trimming, return `null`.
2. Determine once, from the whole normalised word, whether it is "Slavo-Germanic", and whether it starts with a silent letter pair (`GN`, `KN`, `PN`, `WR`, `PS`); if so, scanning starts at the second character, otherwise at the first.
3. Create a key accumulator limited to `getMaxCodeLen()` characters (default 4). Scan the word from the start index; stop as soon as both the primary and the alternate keys have reached the maximum length, or the end of the word is reached.
4. At each position, the current letter decides the action:
   - `A E I O U Y`: vowel handling (delegated) which returns the next index.
   - `B`: append `P`; skip a following `B` as well.
   - `Ç` (C with cedilla): append `S`, advance by one.
   - `C`, `D`, `G`, `H`, `J`, `L`, `P`, `R`, `S`, `T`, `W`, `X`, `Z`: apply the corresponding per-letter rule, which returns the next index. `G`, `J`, `R`, `S` and `Z` also receive the Slavo-Germanic flag.
   - `F`: append `F`; `K`: append `K`; `N`: append `N`; `Q`: append `K`; `V`: append `F`. In each of these cases a doubled letter (the same letter at the next position) is consumed together with the first.
   - `M`: append `M`; advance by two when the special "M" condition holds (an `M` directly followed by `M`, or the "UMB" ending pattern), otherwise by one.
   - `Ñ` (N with tilde): append `N`, advance by one.
   - Any other character (digits, punctuation, other letters): ignored, advance by one.
5. Return the alternate key if `alternate` is `true`, otherwise the primary key.

## 3. Input specification

- `value`: any string, possibly `null`, empty or whitespace-only; may contain non-letters and the characters `Ç` / `Ñ`.
- `alternate`: selects the key to return.

## 4. Output specification

- The primary or alternate key, an upper-case string of at most `getMaxCodeLen()` characters, or `null` for null/blank input.
- Examples (primary / alternate): `"testing"` -> `TSTN` / `TSTN`; `"The"` -> `0` / `T`; `"quick"` -> `KK`; `"brown"` -> `PRN`; `"fox"` -> `FKS`; `"jumped"` -> `JMPT` / `AMPT`; `"MacCafferey"` -> `MKFR`; `"Stephan"` -> `STFN`; `"san jose"` -> `SNHS`; `"ç"` -> `S`; `"ñ"` -> `N`.
- `null`, `""`, `" "` and `"\t\n\r "` all return `null`.

## 5. Edge cases and constraints

- The result does not depend on the default locale.
- With `setMaxCodeLen(n)`, keys are cut to at most `n` characters.
- The method has no side effects on the object (the code length limit is only read).
