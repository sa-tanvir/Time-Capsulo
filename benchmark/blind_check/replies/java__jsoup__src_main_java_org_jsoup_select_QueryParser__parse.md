```java
Evaluator parse() {
    tq.consumeWhitespace();

    if (tq.matchesAny(combinators)) {
        evals.add(new StructuralEvaluator.Root());
        combinator(tq.consume());
    } else {
        findElements();
    }

    while (!tq.isEmpty()) {
        final boolean seenWhite = tq.consumeWhitespace();

        if (tq.matchesAny(combinators)) {
            combinator(tq.consume());
        } else if (seenWhite) {
            combinator(' ');
        } else {
            findElements();
        }
    }

    if (evals.size() == 1)
        return evals.get(0);

    return new CombiningEvaluator.And(evals);
}
```
