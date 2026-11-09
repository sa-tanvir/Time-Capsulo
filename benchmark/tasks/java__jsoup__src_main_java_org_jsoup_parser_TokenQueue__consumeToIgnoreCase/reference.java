public String consumeToIgnoreCase(String seq) {
    int start = pos;
    String first = seq.substring(0, 1);
    boolean canScan = first.toLowerCase().equals(first.toUpperCase()); // if first is not cased, use index of
    while (!isEmpty()) {
        if (matches(seq))
            break;

        if (canScan) {
            int skip = queue.indexOf(first, pos) - pos;
            if (skip == 0) // this char is the skip char, but not match, so force advance of pos
                pos++;
            else if (skip < 0) // no chance of finding, grab to end
                pos = queue.length();
            else
                pos += skip;
        }
        else
            pos++;
    }

    return queue.substring(start, pos);
}
