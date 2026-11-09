public static long[] hash128(final byte[] data, final int offset, final int length, final int seed) {
	long h1 = seed;
	long h2 = seed;
	final int nblocks = length >> 4;

	// body
	for (int i = 0; i < nblocks; i++) {
		final int i16 = i << 4;
		long k1 = ((long) data[offset + i16] & 0xff) | (((long) data[offset + i16 + 1] & 0xff) << 8)
				| (((long) data[offset + i16 + 2] & 0xff) << 16) | (((long) data[offset + i16 + 3] & 0xff) << 24)
				| (((long) data[offset + i16 + 4] & 0xff) << 32) | (((long) data[offset + i16 + 5] & 0xff) << 40)
				| (((long) data[offset + i16 + 6] & 0xff) << 48) | (((long) data[offset + i16 + 7] & 0xff) << 56);

		long k2 = ((long) data[offset + i16 + 8] & 0xff) | (((long) data[offset + i16 + 9] & 0xff) << 8)
				| (((long) data[offset + i16 + 10] & 0xff) << 16) | (((long) data[offset + i16 + 11] & 0xff) << 24)
				| (((long) data[offset + i16 + 12] & 0xff) << 32) | (((long) data[offset + i16 + 13] & 0xff) << 40)
				| (((long) data[offset + i16 + 14] & 0xff) << 48) | (((long) data[offset + i16 + 15] & 0xff) << 56);

		// mix functions for k1
		k1 *= C1;
		k1 = Long.rotateLeft(k1, R1);
		k1 *= C2;
		h1 ^= k1;
		h1 = Long.rotateLeft(h1, R2);
		h1 += h2;
		h1 = h1 * M + N1;

		// mix functions for k2
		k2 *= C2;
		k2 = Long.rotateLeft(k2, R3);
		k2 *= C1;
		h2 ^= k2;
		h2 = Long.rotateLeft(h2, R1);
		h2 += h1;
		h2 = h2 * M + N2;
	}

	// tail
	long k1 = 0;
	long k2 = 0;
	final int tailStart = nblocks << 4;
	switch (length - tailStart) {
	case 15:
		k2 ^= (long) (data[offset + tailStart + 14] & 0xff) << 48;
	case 14:
		k2 ^= (long) (data[offset + tailStart + 13] & 0xff) << 40;
	case 13:
		k2 ^= (long) (data[offset + tailStart + 12] & 0xff) << 32;
	case 12:
		k2 ^= (long) (data[offset + tailStart + 11] & 0xff) << 24;
	case 11:
		k2 ^= (long) (data[offset + tailStart + 10] & 0xff) << 16;
	case 10:
		k2 ^= (long) (data[offset + tailStart + 9] & 0xff) << 8;
	case 9:
		k2 ^= data[offset + tailStart + 8] & 0xff;
		k2 *= C2;
		k2 = Long.rotateLeft(k2, R3);
		k2 *= C1;
		h2 ^= k2;

	case 8:
		k1 ^= (long) (data[offset + tailStart + 7] & 0xff) << 56;
	case 7:
		k1 ^= (long) (data[offset + tailStart + 6] & 0xff) << 48;
	case 6:
		k1 ^= (long) (data[offset + tailStart + 5] & 0xff) << 40;
	case 5:
		k1 ^= (long) (data[offset + tailStart + 4] & 0xff) << 32;
	case 4:
		k1 ^= (long) (data[offset + tailStart + 3] & 0xff) << 24;
	case 3:
		k1 ^= (long) (data[offset + tailStart + 2] & 0xff) << 16;
	case 2:
		k1 ^= (long) (data[offset + tailStart + 1] & 0xff) << 8;
	case 1:
		k1 ^= data[offset + tailStart] & 0xff;
		k1 *= C1;
		k1 = Long.rotateLeft(k1, R1);
		k1 *= C2;
		h1 ^= k1;
	}

	// finalization
	h1 ^= length;
	h2 ^= length;

	h1 += h2;
	h2 += h1;

	h1 = fmix64(h1);
	h2 = fmix64(h2);

	h1 += h2;
	h2 += h1;

	return new long[] { h1, h2 };
}
