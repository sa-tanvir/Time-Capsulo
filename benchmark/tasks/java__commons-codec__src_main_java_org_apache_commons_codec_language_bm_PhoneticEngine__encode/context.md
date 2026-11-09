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
