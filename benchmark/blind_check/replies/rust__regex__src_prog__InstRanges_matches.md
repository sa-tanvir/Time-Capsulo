```rust
pub fn matches(&self, c: Char) -> bool {
    // Fast path for small classes / ASCII-heavy input.
    for r in self.ranges.iter().take(4) {
        if c < r.0 {
            return false;
        }
        if c <= r.1 {
            return true;
        }
    }
    self.ranges
        .binary_search_by(|r| {
            if r.1 < c {
                Ordering::Less
            } else if r.0 > c {
                Ordering::Greater
            } else {
                Ordering::Equal
            }
        })
        .is_ok()
}
```
