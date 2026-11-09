```rust
fn read_varu32(data: &[u8]) -> (u32, usize) {
    let mut n: u32 = 0;
    let mut shift: u32 = 0;
    for (i, &b) in data.iter().enumerate() {
        if b < 0b1000_0000 {
            return (n | (b as u32).wrapping_shl(shift), i + 1);
        }
        n |= ((b & 0b0111_1111) as u32).wrapping_shl(shift);
        shift += 7;
    }
    (0, 0)
}
```
