public static void shift(final byte[] array, int startIndexInclusive, int endIndexExclusive, int offset) {
    if (array == null) {
        return;
    }
    if (startIndexInclusive >= array.length - 1 || endIndexExclusive <= 0) {
        return;
    }
    if (startIndexInclusive < 0) {
        startIndexInclusive = 0;
    }
    if (endIndexExclusive >= array.length) {
        endIndexExclusive = array.length;
    }
    int n = endIndexExclusive - startIndexInclusive;
    if (n <= 1) {
        return;
    }
    offset %= n;
    if (offset < 0) {
        offset += n;
    }
    // For algorithm explanations and proof of O(n) time complexity and O(1) space complexity
    // see https://beradrian.wordpress.com/2015/04/07/shift-an-array-in-on-in-place/
    while (n > 1 && offset > 0) {
        final int n_offset = n - offset;

        if (offset > n_offset) {
            swap(array, startIndexInclusive, startIndexInclusive + n - n_offset,  n_offset);
            n = offset;
            offset -= n_offset;
        } else if (offset < n_offset) {
            swap(array, startIndexInclusive, startIndexInclusive + n_offset,  offset);
            startIndexInclusive += offset;
            n = n_offset;
        } else {
            swap(array, startIndexInclusive, startIndexInclusive + n_offset, offset);
            break;
        }
    }
}
