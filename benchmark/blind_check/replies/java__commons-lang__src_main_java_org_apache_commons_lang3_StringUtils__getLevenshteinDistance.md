```java
public static int getLevenshteinDistance(CharSequence s, CharSequence t, final int threshold) {
    if (s == null || t == null) {
        throw new IllegalArgumentException("Strings must not be null");
    }
    if (threshold < 0) {
        throw new IllegalArgumentException("Threshold must not be negative");
    }
    int n = s.length();
    int m = t.length();
    if (n == 0) {
        return m <= threshold ? m : -1;
    }
    if (m == 0) {
        return n <= threshold ? n : -1;
    }
    if (Math.abs(n - m) > threshold) {
        return -1;
    }
    if (n > m) {
        final CharSequence tmp = s;
        s = t;
        t = tmp;
        final int tmpLen = n;
        n = m;
        m = tmpLen;
    }
    int[] p = new int[n + 1];
    int[] d = new int[n + 1];
    final int boundary = Math.min(n, threshold) + 1;
    for (int i = 0; i < boundary; i++) {
        p[i] = i;
    }
    Arrays.fill(p, boundary, p.length, Integer.MAX_VALUE);
    Arrays.fill(d, Integer.MAX_VALUE);
    for (int j = 1; j <= m; j++) {
        final char tj = t.charAt(j - 1);
        d[0] = j;
        final int min = Math.max(1, j - threshold);
        final int max = j > Integer.MAX_VALUE - threshold ? n : Math.min(n, j + threshold);
        if (min > max) {
            return -1;
        }
        if (min > 1) {
            d[min - 1] = Integer.MAX_VALUE;
        }
        for (int i = min; i <= max; i++) {
            if (s.charAt(i - 1) == tj) {
                d[i] = p[i - 1];
            } else {
                final int best = Math.min(Math.min(d[i - 1], p[i]), p[i - 1]);
                d[i] = best == Integer.MAX_VALUE ? Integer.MAX_VALUE : best + 1;
            }
        }
        final int[] tmp = p;
        p = d;
        d = tmp;
    }
    return p[n] <= threshold ? p[n] : -1;
}
```
