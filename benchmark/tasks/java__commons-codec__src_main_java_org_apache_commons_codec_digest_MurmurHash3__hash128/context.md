# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/digest/MurmurHash3.java`
- **Enclosing scope:** `public final class MurmurHash3`

## Imports / includes available in this file

```
(none)
```

## Other functions defined in the same file (signatures only; you may call them)

```
MurmurHash3::IncrementalHash32::add( final byte [ ] data , int offset , final int length)
MurmurHash3::IncrementalHash32::end()
MurmurHash3::IncrementalHash32::start( final int hash)
MurmurHash3::MurmurHash3()
MurmurHash3::fmix32( final int length , int hash)
MurmurHash3::fmix64( long h)
MurmurHash3::hash128( final String data)
MurmurHash3::hash128( final byte [ ] data)
MurmurHash3::hash32( final String data)
MurmurHash3::hash32( final byte [ ] data , final int length , final int seed)
MurmurHash3::hash32( final byte [ ] data , final int length)
MurmurHash3::hash32( final byte [ ] data , final int offset , final int length , final int seed)
MurmurHash3::hash32( final byte [ ] data)
MurmurHash3::hash32( final long l0 , final int seed)
MurmurHash3::hash32( final long l0 , final long l1 , final int seed)
MurmurHash3::hash32( final long l0 , final long l1)
MurmurHash3::hash32( final long l0)
MurmurHash3::hash64( final byte [ ] data , final int offset , final int length , final int seed)
MurmurHash3::hash64( final byte [ ] data , final int offset , final int length)
MurmurHash3::hash64( final byte [ ] data)
MurmurHash3::hash64( final int data)
MurmurHash3::hash64( final long data)
MurmurHash3::hash64( final short data)
MurmurHash3::mix32( int k , int hash)
MurmurHash3::orBytes( final byte b1 , final byte b2 , final byte b3 , final byte b4)
```

## Constants and helpers used by the 128-bit hash

```
private static final long C1 = 0x87c37b91114253d5L;
private static final long C2 = 0x4cf5ad432745937fL;
private static final int R1 = 31;
private static final int R2 = 27;
private static final int R3 = 33;
private static final int M = 5;
private static final int N1 = 0x52dce729;
private static final int N2 = 0x38495ab5;

private static long fmix64(long h) {
    h ^= (h >>> 33);
    h *= 0xff51afd7ed558ccdL;
    h ^= (h >>> 33);
    h *= 0xc4ceb9fe1a85ec53L;
    h ^= (h >>> 33);
    return h;
}
```

`Long.rotateLeft(long, int)` performs `rotl`.
