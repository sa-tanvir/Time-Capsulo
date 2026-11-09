# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/language/DoubleMetaphone.java`
- **Enclosing scope:** `public class DoubleMetaphone implements StringEncoder`

## Imports / includes available in this file

```
import org.apache.commons.codec.EncoderException;
import org.apache.commons.codec.StringEncoder;
import org.apache.commons.codec.binary.StringUtils;
```

## Other functions defined in the same file (signatures only; you may call them)

```
DoubleMetaphone::DoubleMetaphone()
DoubleMetaphone::DoubleMetaphoneResult::DoubleMetaphoneResult( final int maxLength)
DoubleMetaphone::DoubleMetaphoneResult::append( final String primary , final String alternate)
DoubleMetaphone::DoubleMetaphoneResult::append( final String value)
DoubleMetaphone::DoubleMetaphoneResult::append( final char primary , final char alternate)
DoubleMetaphone::DoubleMetaphoneResult::append( final char value)
DoubleMetaphone::DoubleMetaphoneResult::appendAlternate( final String value)
DoubleMetaphone::DoubleMetaphoneResult::appendAlternate( final char value)
DoubleMetaphone::DoubleMetaphoneResult::appendPrimary( final String value)
DoubleMetaphone::DoubleMetaphoneResult::appendPrimary( final char value)
DoubleMetaphone::DoubleMetaphoneResult::getAlternate()
DoubleMetaphone::DoubleMetaphoneResult::getPrimary()
DoubleMetaphone::DoubleMetaphoneResult::isComplete()
DoubleMetaphone::charAt( final String value , final int index)
DoubleMetaphone::cleanInput( String input)
DoubleMetaphone::conditionC0( final String value , final int index)
DoubleMetaphone::conditionCH0( final String value , final int index)
DoubleMetaphone::conditionCH1( final String value , final int index)
DoubleMetaphone::conditionL0( final String value , final int index)
DoubleMetaphone::conditionM0( final String value , final int index)
DoubleMetaphone::contains( final String value , final int start , final int length , final String ... criteria)
DoubleMetaphone::doubleMetaphone( final String value)
DoubleMetaphone::encode( final Object obj)
DoubleMetaphone::encode( final String value)
DoubleMetaphone::getMaxCodeLen()
DoubleMetaphone::handleAEIOUY( final DoubleMetaphoneResult result , final int index)
DoubleMetaphone::handleC( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleCC( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleCH( final String value , final DoubleMetaphoneResult result , final int index)
DoubleMetaphone::handleD( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleG( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::handleGH( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleH( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleJ( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::handleL( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleP( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleR( final String value , final DoubleMetaphoneResult result , final int index , final boolean slavoGermanic)
DoubleMetaphone::handleS( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::handleSC( final String value , final DoubleMetaphoneResult result , final int index)
DoubleMetaphone::handleT( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleW( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleX( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleZ( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::isDoubleMetaphoneEqual( final String value1 , final String value2 , final boolean alternate)
DoubleMetaphone::isDoubleMetaphoneEqual( final String value1 , final String value2)
DoubleMetaphone::isSilentStart( final String value)
DoubleMetaphone::isSlavoGermanic( final String value)
DoubleMetaphone::isVowel( final char ch)
DoubleMetaphone::setMaxCodeLen( final int maxCodeLen)
```

## Instance state

- `maxCodeLen` (`int`, private, default 4): maximum length of each key; read through `getMaxCodeLen()`, changed with `setMaxCodeLen(int)`.
- Constants: `VOWELS = "AEIOU"`, `SILENT_START = {"GN", "KN", "PN", "WR", "PS"}` (used by `isSilentStart`).
- `DoubleMetaphoneResult` (inner class): `new DoubleMetaphoneResult(int maxLength)`; `append(char)` / `append(char, char)` / `append(String)` / `append(String, String)` add to both keys (or to primary and alternate separately); `appendPrimary`, `appendAlternate`; `getPrimary()`, `getAlternate()`; `isComplete()` is true once both keys have reached `maxLength`. Appending never makes a key longer than `maxLength`.
- Each `handleX(...)` helper takes the (normalised) word, the result accumulator and the current index (plus the Slavo-Germanic flag for G, J, R, S, Z) and returns the next index to examine. `handleAEIOUY(result, index)` takes no word.
- `charAt(value, index)` returns `Character.MIN_VALUE` for out-of-range indexes.
