# Functional specification

## 1. Component overview

`ColognePhonetic.colognePhonetic(String text)` encodes a (mostly German) word or name with the Cologne phonetics (Koelner Phonetik): letters are replaced by digit codes so that similarly sounding words obtain the same code. The result is a string of digits `0`-`8`.

## 2. Functional requirements

1. `null` input gives `null`.
2. The text is first normalised by the existing helper `preprocess(String)` (upper-case using German rules, umlauts transcribed to plain vowels), which returns a `char[]`. Every character of the normalised text that is not in `A`..`Z` is skipped: it produces no code and it does not count as a "previous letter".
3. Every remaining letter is translated to a code depending on the letter, on the character that directly follows it in the normalised text (`next`; "none" at the end of the text; this may be a non-letter, which then simply matches none of the listed letters) and on the letter that was handled just before it (`last`; "none" at the start). `last` is the previous `A`..`Z` letter itself, whether or not it produced a code (so `H` can be a `last`).

| Letter | Code appended |
|---|---|
| `A E I J O U Y` | `0` |
| `H` | none (but see rule 4) |
| `B` | `1` |
| `P`, when `next` is not `H` | `1` |
| `P`, when `next` is `H` | `3` |
| `F V W` | `3` |
| `D` or `T`, when `next` is not `C`, `S` or `Z` | `2` |
| `D` or `T`, when `next` is `C`, `S` or `Z` | `8` |
| `G K Q` | `4` |
| `X`, when `last` is not `C`, `K` or `Q` | `4` then `8` |
| `X`, when `last` is `C`, `K` or `Q` | `8` |
| `S Z` | `8` |
| `C` when no code has been produced yet in the result | `4` if `next` is one of `A H K L O Q R U X`, otherwise `8` |
| `C` when at least one code has been produced | `8` if `last` is `S` or `Z`, or if `next` is not one of `A H K O Q U X`; otherwise `4` |
| `R` | `7` |
| `L` | `5` |
| `M N` | `6` |

4. A code is actually appended to the result only if (a) it differs from the code produced for the immediately preceding letter (consecutive identical codes collapse into one; a letter that produces no code such as `H` still counts as "the previous code", with a value that differs from every digit, so identical codes separated by an `H` are both kept; the two digits of `X` are each subject to this rule), and (b) it is not `0`, unless the result is still empty. In other words `0` can only be the first character of the output.

## 3. Input specification

`text`: any string or `null`. Characters outside `A`-`Z` after normalisation (digits, hyphens, spaces, other alphabets) are ignored.

## 4. Output specification

- `null` for `null` input; an empty string when no letter yields a code.
- Otherwise the string of digit codes after rule 4.
- Examples: `"Müller-Lüdenscheidt"` -> `"65752682"`; `"Breschnew"` -> `"17863"`; `"Wikipedia"` -> `"3412"`; `"Meyer"` -> `"67"`; `"Xaver"` -> `"4837"`; `"Aabjoe"` -> `"01"`; `"Aaclan"` -> `"0856"`; `"Aychlmajr"` -> `"04567"`; `"a"`, `"e"`, `"i"` -> `"0"`.

## 5. Edge cases and constraints

- Case-insensitive; `"ä"`, `"ö"`, `"ü"` behave like `A`, `O`, `U`; the sharp s becomes `SS`.
- Hyphens and other non-letters between two letters that yield the same code do not prevent those codes from collapsing.
- The method does not modify any state and is thread-safe.
