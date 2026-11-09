```java
private static LevenshteinResults limitedCompare(CharSequence left,
                                                 CharSequence right,
                                                 final int threshold) {
    if (left == null || right == null) {
        throw new IllegalArgumentException("CharSequences must not be null");
    }
    if (threshold < 0) {
        throw new IllegalArgumentException("Threshold must not be negative");
    }
    int n = left.length();
    int m = right.length();
    if (n == 0) {
        return m <= threshold ? new LevenshteinResults(m, m, 0, 0) : new LevenshteinResults(-1, 0, 0, 0);
    }
    if (m == 0) {
        return n <= threshold ? new LevenshteinResults(n, 0, n, 0) : new LevenshteinResults(-1, 0, 0, 0);
    }
    boolean swapped = false;
    if (n > m) {
        final CharSequence tmp = left;
        left = right;
        right = tmp;
        n = m;
        m = right.length();
        swapped = true;
    }
    if (m - n > threshold) {
        return new LevenshteinResults(-1, 0, 0, 0);
    }
    int[] p = new int[n + 1];
    int[] d = new int[n + 1];
    int[] tempD;
    final int[][] matrix = new int[m + 1][n + 1];
    for (int index = 0; index <= n; index++) {
        matrix[0][index] = index;
    }
    for (int index = 0; index <= m; index++) {
        matrix[index][0] = index;
    }
    final int boundary = Math.min(n, threshold) + 1;
    for (int i = 0; i < boundary; i++) {
        p[i] = i;
    }
    Arrays.fill(p, boundary, p.length, Integer.MAX_VALUE);
    Arrays.fill(d, Integer.MAX_VALUE);
    for (int j = 1; j <= m; j++) {
        final char rightJ = right.charAt(j - 1);
        d[0] = j;
        final int min = Math.max(1, j - threshold);
        final int max = j > Integer.MAX_VALUE - threshold ? n : Math.min(n, j + threshold);
        if (min > 1) {
            d[min - 1] = Integer.MAX_VALUE;
        }
        int lowerBound = Integer.MAX_VALUE;
        for (int i = min; i <= max; i++) {
            if (left.charAt(i - 1) == rightJ) {
                d[i] = p[i - 1];
            } else {
                d[i] = 1 + Math.min(Math.min(d[i - 1], p[i]), p[i - 1]);
            }
            lowerBound = Math.min(lowerBound, d[i]);
            matrix[j][i] = d[i];
        }
        if (lowerBound > threshold) {
            return new LevenshteinResults(-1, 0, 0, 0);
        }
        tempD = p;
        p = d;
        d = tempD;
    }
    if (p[n] <= threshold) {
        return findDetailedResults(left, right, matrix, swapped);
    }
    return new LevenshteinResults(-1, 0, 0, 0);
}
```
