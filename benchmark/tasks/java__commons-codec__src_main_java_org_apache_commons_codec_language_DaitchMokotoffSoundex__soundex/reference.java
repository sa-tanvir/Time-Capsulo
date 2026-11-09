private String[] soundex(final String source, final boolean branching) {
    if (source == null) {
        return null;
    }

    final String input = cleanup(source);

    final Set<Branch> currentBranches = new LinkedHashSet<>();
    currentBranches.add(new Branch());

    char lastChar = '\0';
    for (int index = 0; index < input.length(); index++) {
        final char ch = input.charAt(index);

        // ignore whitespace inside a name
        if (Character.isWhitespace(ch)) {
            continue;
        }

        final String inputContext = input.substring(index);
        final List<Rule> rules = RULES.get(ch);
        if (rules == null) {
            continue;
        }

        // use an EMPTY_LIST to avoid false positive warnings wrt potential null pointer access
        final List<Branch> nextBranches = branching ? new ArrayList<Branch>() : Collections.<Branch>emptyList();

        for (final Rule rule : rules) {
            if (rule.matches(inputContext)) {
                if (branching) {
                    nextBranches.clear();
                }
                final String[] replacements = rule.getReplacements(inputContext, lastChar == '\0');
                final boolean branchingRequired = replacements.length > 1 && branching;

                for (final Branch branch : currentBranches) {
                    for (final String nextReplacement : replacements) {
                        // if we have multiple replacements, always create a new branch
                        final Branch nextBranch = branchingRequired ? branch.createBranch() : branch;

                        // special rule: occurrences of mn or nm are treated differently
                        final boolean force = (lastChar == 'm' && ch == 'n') || (lastChar == 'n' && ch == 'm');

                        nextBranch.processNextReplacement(nextReplacement, force);

                        if (branching) {
                            nextBranches.add(nextBranch);
                        } else {
                            break;
                        }
                    }
                }

                if (branching) {
                    currentBranches.clear();
                    currentBranches.addAll(nextBranches);
                }
                index += rule.getPatternLength() - 1;
                break;
            }
        }

        lastChar = ch;
    }

    final String[] result = new String[currentBranches.size()];
    int index = 0;
    for (final Branch branch : currentBranches) {
        branch.finish();
        result[index++] = branch.toString();
    }

    return result;
}
