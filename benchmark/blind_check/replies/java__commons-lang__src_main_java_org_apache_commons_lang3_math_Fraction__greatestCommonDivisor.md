```java
private static int greatestCommonDivisor(int u, int v) {
    if (u == 0 || v == 0) {
        if (u == Integer.MIN_VALUE || v == Integer.MIN_VALUE) {
            throw new ArithmeticException("overflow: gcd is 2^31");
        }
        return Math.abs(u) + Math.abs(v);
    }
    if (Math.abs(u) == 1 || Math.abs(v) == 1) {
        return 1;
    }
    long a = Math.abs((long) u);
    long b = Math.abs((long) v);
    final int shift = Long.numberOfTrailingZeros(a | b);
    a >>= Long.numberOfTrailingZeros(a);
    while (b != 0) {
        b >>= Long.numberOfTrailingZeros(b);
        if (a > b) {
            final long tmp = a;
            a = b;
            b = tmp;
        }
        b -= a;
    }
    final long result = a << shift;
    if (result == (1L << 31)) {
        throw new ArithmeticException("overflow: gcd is 2^31");
    }
    return (int) result;
}
```
