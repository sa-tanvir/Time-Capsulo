```java
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
    if (endIndexExclusive > array.length) {
        endIndexExclusive = array.length;
    }
    final int n = endIndexExclusive - startIndexInclusive;
    if (n <= 1) {
        return;
    }
    offset %= n;
    if (offset < 0) {
        offset += n;
    }
    if (offset == 0) {
        return;
    }
    // rotate right by offset using three in-place reversals
    final int[] from = {startIndexInclusive, startIndexInclusive, startIndexInclusive + offset};
    final int[] to = {endIndexExclusive - 1, startIndexInclusive + offset - 1, endIndexExclusive - 1};
    for (int r = 0; r < 3; r++) {
        int i = from[r];
        int j = to[r];
        while (i < j) {
            final byte tmp = array[i];
            array[i++] = array[j];
            array[j--] = tmp;
        }
    }
}
```
