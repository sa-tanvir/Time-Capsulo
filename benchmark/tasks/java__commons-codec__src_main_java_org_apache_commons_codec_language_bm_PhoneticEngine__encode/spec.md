# Functional specification

## 1. Component overview

`PhoneticEngine.encode(String input, Languages.LanguageSet languageSet)` converts a name into its Beider-Morse phonetic representation: a string of phonemes in which alternatives are separated by `|` and, for names that are encoded in several parts, parts are separated by `-` (with parentheses in some cases). The behaviour depends on the engine's name type (`GENERIC`, `ASHKENAZI`, `SEPHARDIC`), rule type (`APPROX` or `EXACT`), the `concat` flag and the set of possible source languages.

## 2. Functional requirements

1. **Rule sets.** Obtain, from `Rule.getInstanceMap`, (a) the language-specific main rules for `(nameType, RuleType.RULES, languageSet)`, (b) the common final rules for `(nameType, ruleType, "common")` and (c) the language-specific final rules for `(nameType, ruleType, languageSet)`.
2. **Tidying.** The input is lower-cased with `Locale.ENGLISH`, every `-` is replaced by a space and leading/trailing whitespace is removed.
3. **Generic prefixes** (only when the name type is `GENERIC`):
   - If the tidied input is at least two characters long and starts with `d'`: let `remainder` be the input without these two characters and `combined` be `"d"` + `remainder`; return `"(" + encode(remainder) + ")-(" + encode(combined) + ")"` where `encode(String)` is the engine's one-argument encode (it guesses the languages itself).
   - Otherwise, for each name prefix `l` of the engine's name type (`NAME_PREFIXES`) in iteration order: if the input starts with `l` followed by a space, let `remainder` be the input without the prefix and the space, `combined` be `l + remainder`, and return `"(" + encode(remainder) + ")-(" + encode(combined) + ")"`.
4. **Words.** Split the tidied input on runs of whitespace into `words`. Build `words2` depending on the name type:
   - `SEPHARDIC`: for every word, keep only the part after the last apostrophe (`'`); then remove all entries that are name prefixes of the type (all occurrences, by value).
   - `ASHKENAZI`: all words, with all name prefixes of the type removed.
   - `GENERIC`: all words unchanged.
5. **Choice of text to encode.**
   - If `concat` is true: the text is `words2` joined with single spaces.
   - Else if `words2` has exactly one entry: the text is the **first element of `words`** (the first word of the split input, before apostrophe stripping and prefix removal).
   - Else (several words): encode each entry of `words2` separately with the one-argument `encode(String)` and return the results joined by `-` (no leading `-`).
6. **Phoneme construction.** Start from an empty phoneme builder for the language set (`PhonemeBuilder.empty(languageSet)`). Walk through the text from index 0; at each index apply the main rules via `RulesApplication(rules, text, builder, i, maxPhonemes).invoke()`, which yields the new index and the new builder (it handles one rule match per step; the index is advanced by the helper).
7. **Final rules.** Apply `applyFinalRules(builder, finalRules1)` (common rules), then `applyFinalRules(builder, finalRules2)` (language-specific rules).
8. Return `builder.makeString()`: the phonemes of the final builder joined with `|`.

## 3. Input specification

- `input`: a non-null name; may contain several words separated by spaces or dashes, apostrophes, upper case letters.
- `languageSet`: a non-null `Languages.LanguageSet` (for example `Languages.ANY_LANGUAGE` or a set guessed by `Lang.guessLanguages`).

## 4. Output specification

A string of phoneme alternatives separated by `|`; for several words or prefix variants the `-`-joined form described above. An input that produces no phonemes yields an empty string.

## 5. Edge cases and constraints

- The engine does not hold mutable state; concurrent use is safe.
- The recursion in steps 3 and 5 calls the one-argument `encode`, which guesses its own languages, so the passed `languageSet` only affects the part encoded directly.
- No locale dependence (lower-casing uses `Locale.ENGLISH`).
