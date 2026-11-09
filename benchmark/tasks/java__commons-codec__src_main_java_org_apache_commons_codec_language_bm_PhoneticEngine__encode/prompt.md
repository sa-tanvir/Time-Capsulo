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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/language/bm/PhoneticEngine.java`
- **Enclosing scope:** `static final class PhonemeBuilder`

## Imports / includes available in this file

```
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import org.apache.commons.codec.language.bm.Languages.LanguageSet;
import org.apache.commons.codec.language.bm.Rule.Phoneme;
```

## Other functions defined in the same file (signatures only; you may call them)

```
PhoneticEngine::PhonemeBuilder::PhonemeBuilder( final Rule . Phoneme phoneme)
PhoneticEngine::PhonemeBuilder::PhonemeBuilder( final Set<Rule.Phoneme> phonemes)
PhoneticEngine::PhonemeBuilder::append( final CharSequence str)
PhoneticEngine::PhonemeBuilder::apply( final Rule . PhonemeExpr phonemeExpr , final int maxPhonemes)
PhoneticEngine::PhonemeBuilder::empty( final Languages . LanguageSet languages)
PhoneticEngine::PhonemeBuilder::getPhonemes()
PhoneticEngine::PhonemeBuilder::makeString()
PhoneticEngine::PhoneticEngine( final NameType nameType , final RuleType ruleType , final boolean concat , final int maxPhonemes)
PhoneticEngine::PhoneticEngine( final NameType nameType , final RuleType ruleType , final boolean concat)
PhoneticEngine::RulesApplication::RulesApplication( final Map<String,List<Rule>> finalRules , final CharSequence input , final PhonemeBuilder phonemeBuilder , final int i , final int maxPhonemes)
PhoneticEngine::RulesApplication::getI()
PhoneticEngine::RulesApplication::getPhonemeBuilder()
PhoneticEngine::RulesApplication::invoke()
PhoneticEngine::RulesApplication::isFound()
PhoneticEngine::applyFinalRules( final PhonemeBuilder phonemeBuilder , final Map<String,List<Rule>> finalRules)
PhoneticEngine::encode( final String input)
PhoneticEngine::getLang()
PhoneticEngine::getMaxPhonemes()
PhoneticEngine::getNameType()
PhoneticEngine::getRuleType()
PhoneticEngine::isConcat()
PhoneticEngine::join( final Iterable<String> strings , final String sep)
```

## Instance state and constants

- `nameType` (`NameType`), `ruleType` (`RuleType`, `APPROX` or `EXACT`), `concat` (`boolean`), `maxPhonemes` (`int`, default 20), `lang` (`Lang`) are private final fields set by the constructor.
- `NAME_PREFIXES` (`private static final Map<NameType, Set<String>>`):
  - `ASHKENAZI`: `bar, ben, da, de, van, von`
  - `SEPHARDIC`: `al, el, da, dal, de, del, dela, de la, della, des, di, do, dos, du, van, von`
  - `GENERIC`: `da, dal, de, del, dela, de la, della, des, di, do, dos, du, van, von`
- `private static String join(Iterable<String> strings, String sep)`: concatenates with the separator between elements.
- `private PhonemeBuilder applyFinalRules(PhonemeBuilder builder, Map<String, List<Rule>> finalRules)`: applies the final rules to every phoneme of the builder and returns the new builder (throws `NullPointerException` if `finalRules` is null).
- `RulesApplication(Map<String, List<Rule>> rules, CharSequence input, PhonemeBuilder builder, int i, int maxPhonemes)` with `invoke()` returning itself, `getI()` (next index) and `getPhonemeBuilder()`.
- `PhonemeBuilder.empty(Languages.LanguageSet)`, `makeString()`.
- `Rule.getInstanceMap(NameType, RuleType, Languages.LanguageSet)` and `Rule.getInstanceMap(NameType, RuleType, String language)` return the rule table (`Map<String, List<Rule>>`).

=== STUB ===
```java
public String encode(String input, final Languages.LanguageSet languageSet) {
    // TODO: implement according to the specification
}
```
