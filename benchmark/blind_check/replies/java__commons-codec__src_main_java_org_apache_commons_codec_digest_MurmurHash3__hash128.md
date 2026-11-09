```java
public static long[] hash128(final byte[] data, final int offset, final int length, final int seed) {
    long h1 = seed;
    long h2 = seed;
    final int nblocks = length >> 4;

    for (int i = 0; i < nblocks; i++) {
        final int index = offset + (i << 4);
        long k1 = 0;
        long k2 = 0;
        for (int j = 7; j >= 0; j--) {
            k1 = (k1 << 8) | (data[index + j] & 0xffL);
            k2 = (k2 << 8) | (data[index + 8 + j] & 0xffL);
        }

        k1 *= C1;
        k1 = Long.rotateLeft(k1, R1);
        k1 *= C2;
        h1 ^= k1;
        h1 = Long.rotateLeft(h1, R2);
        h1 += h2;
        h1 = h1 * M + N1;

        k2 *= C2;
        k2 = Long.rotateLeft(k2, R3);
        k2 *= C1;
        h2 ^= k2;
        h2 = Long.rotateLeft(h2, R1);
        h2 += h1;
        h2 = h2 * M + N2;
    }

    final int tailStart = offset + (nblocks << 4);
    final int tail = length & 15;
    long k1 = 0;
    long k2 = 0;
    for (int i = tail - 1; i >= 8; i--) {
        k2 = (k2 << 8) | (data[tailStart + i] & 0xffL);
    }
    for (int i = Math.min(tail, 8) - 1; i >= 0; i--) {
        k1 = (k1 << 8) | (data[tailStart + i] & 0xffL);
    }
    if (tail > 8) {
        k2 *= C2;
        k2 = Long.rotateLeft(k2, R3);
        k2 *= C1;
        h2 ^= k2;
    }
    if (tail > 0) {
        k1 *= C1;
        k1 = Long.rotateLeft(k1, R1);
        k1 *= C2;
        h1 ^= k1;
    }

    h1 ^= length;
    h2 ^= length;
    h1 += h2;
    h2 += h1;
    h1 = fmix64(h1);
    h2 = fmix64(h2);
    h1 += h2;
    h2 += h1;

    return new long[] {h1, h2};
}
```
