# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/select/QueryParser.java`
- **Enclosing scope:** `public class QueryParser`

## Imports / includes available in this file

```
import org.jsoup.internal.StringUtil;
import org.jsoup.helper.Validate;
import org.jsoup.parser.TokenQueue;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import static org.jsoup.internal.Normalizer.normalize;
```

## Other functions defined in the same file (signatures only; you may call them)

```
QueryParser::QueryParser( String query)
QueryParser::allElements()
QueryParser::byAttribute()
QueryParser::byClass()
QueryParser::byId()
QueryParser::byTag()
QueryParser::combinator( char combinator)
QueryParser::consumeIndex()
QueryParser::consumeSubQuery()
QueryParser::contains( boolean own)
QueryParser::containsData()
QueryParser::cssNthChild( boolean backwards , boolean ofType)
QueryParser::findElements()
QueryParser::has()
QueryParser::indexEquals()
QueryParser::indexGreaterThan()
QueryParser::indexLessThan()
QueryParser::matches( boolean own)
QueryParser::not()
QueryParser::parse( String query)
```

## Instance state

Fields of `QueryParser` (private constructor; instances are created by the static `parse(String)`):

- `tq` (`TokenQueue`, private): the unread part of the query. Useful methods: `consumeWhitespace()` (consumes whitespace; returns true if any was consumed), `matchesAny(String...)` / `matchesAny(char...)` (true if the next character(s) match one of the options), `consume()` (returns the next char), `isEmpty()`.
- `query` (`String`): the original query (used in error messages).
- `evals` (`List<Evaluator>`, private): evaluators collected so far; `findElements()` and `combinator(char)` append to / replace its contents.
- `combinators` (`private static final String[]`) = `{",", ">", "+", "~", " "}`. Pass it to `tq.matchesAny(String...)`; note that because whitespace is consumed first, the space entry only matters for the descendant case handled by the loop itself.

Evaluator classes: `StructuralEvaluator.Root` (no-arg constructor), `CombiningEvaluator.And(Collection<Evaluator>)`.
