# Functional specification

## 1. Component overview

`Soundex.soundex(String str)` computes the Soundex code of a word: a four-character string made of the first letter of the word followed by three digits, describing how the rest of the word sounds. The letter-to-digit table and the treatment of the letters `H` and `W` depend on the `Soundex` instance (see "Instance state" in the context).

## 2. Functional requirements

1. `null` input returns `null`.
2. Clean the input: remove every character that is not a letter (`Character.isLetter`) and convert the rest to upper case with `Locale.ENGLISH`. The helper `SoundexUtils.clean(String)` of the same package does exactly this and may be called. If the cleaned string is empty, return it (the empty string).
3. The result has exactly four characters and starts with the first letter of the cleaned string. The remaining positions are filled with digit codes and padded with `'0'` characters.
4. Digit codes are obtained from the instance's mapping via the helper `map(char)` (which maps `'A'`..`'Z'` to a mapping character). Starting with the second letter of the cleaned string and moving left to right, until the four positions are filled:
   - If the instance treats `H` and `W` specially (see state), the letters `H` and `W` are skipped entirely: they produce no digit and do not change the "previous digit".
   - The code of the letter is looked up with `map`. If it is the silent marker `'-'`, the letter is skipped (it produces no digit and does not change the "previous digit" either).
   - A code is appended to the result only if it is not `'0'` and differs from the "previous digit". The "previous digit" is then set to this code. A `'0'` code (a vowel in the default table) is not appended but does become the "previous digit", so equal codes separated by a vowel are both kept.
   - The "previous digit" starts as the code of the first letter (even though the first letter itself is emitted as a letter).
5. Letters outside `A`..`Z` (for example `'É'`) are not mapped: `map` throws `IllegalArgumentException` with a message of the form `The character is not mapped: <char> (index=<n>)` where `<n>` is `char - 'A'`. This happens for any such letter that is examined (including the first letter), so the exception can only be avoided for letters after the fourth output position is already filled.

## 3. Input specification

Any string or `null`.

## 4. Output specification

A 4-character string, the empty string, or `null` as described. Examples with the default instance: `"Robert"` -> `R163`; `"Rupert"` -> `R163`; `"Rubin"` -> `R150`; `"Ashcraft"` -> `A261`; `"Tymczak"` -> `T522`; `"Pfister"` -> `P236`; `"Lee"` -> `L000`; `"A"` -> `A000`; `"  "` -> `""`.

## 5. Edge cases and constraints

- The method reads only immutable instance state, so it is thread-safe.
- Input case and non-letter characters (digits, spaces, punctuation) do not matter.
