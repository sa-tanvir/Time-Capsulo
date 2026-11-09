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

`QueryParser.parse()` (instance method) turns the CSS-like selector held in the parser into a single `Evaluator` tree, handling the combinators (descendant, child, sibling and "or") and implicit AND of simple selectors. The public static `QueryParser.parse(String)` creates a parser over the query and calls it.

## 2. Functional requirements

State: `tq` is a `TokenQueue` over the query; `evals` is a `List<Evaluator>` (initially empty) that collects the evaluators built so far. The combinator characters are `,` `>` `+` `~` and the space.

1. Skip leading whitespace in the queue.
2. If the queue now starts with a combinator character (`,`, `>`, `+`, `~`), add a `StructuralEvaluator.Root` evaluator to `evals` and consume that combinator character, applying it as a combinator (see below). Otherwise read the first compound element selector with the element-reading helper.
3. While the queue is not empty: consume any whitespace (remember whether some was consumed). Then:
   - if the queue starts with a combinator character, consume it and apply it as a combinator;
   - else if whitespace had been consumed, apply the descendant combinator (space);
   - else read the next simple selector (such as `.class`, `#id`, `[attr]`, `:pseudo`, or a tag) with the element-reading helper; it adds to `evals`, which means the simple selectors of one compound selector are ANDed.
4. Finally: if `evals` contains exactly one evaluator, return it; otherwise return a `CombiningEvaluator.And` over all evaluators in `evals` (an empty list gives an `And` with no evaluators).

The class already has these helpers, which you must use rather than re-implement: `findElements()` reads one simple selector from `tq` and appends the evaluator for it to `evals` (and throws `Selector.SelectorParseException` for text that is not a selector); `combinator(char)` consumes the sub-query to the right of a combinator and merges it with the current `evals` into one evaluator according to the combinator and operator precedence (a comma binds loosest: `a b, c d` is an `Or` of two `And`s), leaving a single evaluator in `evals`; `consumeSubQuery()` reads text up to the next top-level combinator.

## 3. Input specification

The query string may be empty, contain extra spaces, nested parentheses and brackets, quotes, and up to thousands of characters and hundreds of combinators. Errors raised by the helpers (unparseable text, unbalanced brackets or quotes such as `a[href="]`, `p:contains(One " One)`) propagate out of this method unchanged; the static `parse(String)` wrapper converts `IllegalArgumentException` to `Selector.SelectorParseException`.

## 4. Output specification

An `Evaluator`. Examples: `a b, c d, e f` returns an `Or` with three `And` children, each holding a `Tag` evaluator and a `StructuralEvaluator.Parent`; `.foo > ol, ol > li + li` returns an `Or` with two `And`s whose string forms are `ol :ImmediateParent.foo` and `li :prevli :ImmediateParentol`; `div` returns a single `Tag` evaluator; `> a` returns an `And` starting from the `Root` evaluator; `p.c1` returns an `And` of a tag and a class evaluator.

## 5. Edge cases and constraints

- Whitespace around combinators is insignificant (`p>a`, `p > a` and `p   >   a` are equivalent).
- The method consumes the whole queue (or throws). It runs in time linear in the query length plus the work done by the helpers.

=== CONTEXT ===
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

=== STUB ===
```java
Evaluator parse() {
    // TODO: implement according to the specification
}
```
