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
