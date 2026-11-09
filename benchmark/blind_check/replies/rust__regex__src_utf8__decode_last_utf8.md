```rust
pub fn decode_last_utf8(src: &[u8]) -> Option<(char, usize)> {
    if src.is_empty() {
        return None;
    }
    let mut start = src.len() - 1;
    let limit = src.len().saturating_sub(4);
    while start > limit && !is_start_byte(src[start]) {
        start -= 1;
    }
    match decode_utf8(&src[start..]) {
        None => None,
        Some((_, n)) if n < src.len() - start => None,
        Some((cp, n)) => Some((cp, n)),
    }
}
```
