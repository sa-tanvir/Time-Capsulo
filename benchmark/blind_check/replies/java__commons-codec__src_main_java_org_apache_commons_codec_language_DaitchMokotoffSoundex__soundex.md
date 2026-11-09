```java
private String[] soundex(final String source, final boolean branching) {
    if (source == null) {
        return null;
    }
    final String input = cleanup(source);
    List<Branch> current = new ArrayList<>();
    current.add(new Branch());
    char lastChar = '\0';
    for (int index = 0; index < input.length(); index++) {
        final char ch = input.charAt(index);
        if (Character.isWhitespace(ch)) {
            continue;
        }
        final String inputContext = input.substring(index);
        final List<Rule> rules = RULES.get(ch);
        if (rules == null) {
            continue;
        }
        for (final Rule rule : rules) {
            if (rule.matches(inputContext)) {
                final String[] replacements = rule.getReplacements(inputContext, lastChar == '\0');
                final boolean branchingRequired = branching && replacements.length > 1;
                final boolean force = (lastChar == 'm' && ch == 'n') || (lastChar == 'n' && ch == 'm');
                if (branching) {
                    final Set<Branch> next = new LinkedHashSet<>();
                    for (final Branch branch : current) {
                        for (final String replacement : replacements) {
                            final Branch nextBranch = branchingRequired ? branch.createBranch() : branch;
                            nextBranch.processNextReplacement(replacement, force);
                            next.add(nextBranch);
                        }
                    }
                    current = new ArrayList<>(next);
                } else {
                    for (final Branch branch : current) {
                        branch.processNextReplacement(replacements[0], force);
                    }
                }
                index += rule.getPatternLength() - 1;
                break;
            }
        }
        lastChar = ch;
    }
    final String[] result = new String[current.size()];
    for (int i = 0; i < result.length; i++) {
        final Branch branch = current.get(i);
        branch.finish();
        result[i] = branch.toString();
    }
    return result;
}
```
