private void buildScript(final int start1, final int end1, final int start2, final int end2,
        final EditScript<Character> script) {
    final Snake middle = getMiddleSnake(start1, end1, start2, end2);

    if (middle == null
            || middle.getStart() == end1 && middle.getDiag() == end1 - end2
            || middle.getEnd() == start1 && middle.getDiag() == start1 - start2) {

        int i = start1;
        int j = start2;
        while (i < end1 || j < end2) {
            if (i < end1 && j < end2 && left.charAt(i) == right.charAt(j)) {
                script.append(new KeepCommand<>(left.charAt(i)));
                ++i;
                ++j;
            } else {
                if (end1 - start1 > end2 - start2) {
                    script.append(new DeleteCommand<>(left.charAt(i)));
                    ++i;
                } else {
                    script.append(new InsertCommand<>(right.charAt(j)));
                    ++j;
                }
            }
        }

    } else {

        buildScript(start1, middle.getStart(),
                    start2, middle.getStart() - middle.getDiag(),
                    script);
        for (int i = middle.getStart(); i < middle.getEnd(); ++i) {
            script.append(new KeepCommand<>(left.charAt(i)));
        }
        buildScript(middle.getEnd(), end1,
                    middle.getEnd() - middle.getDiag(), end2,
                    script);
    }
}
