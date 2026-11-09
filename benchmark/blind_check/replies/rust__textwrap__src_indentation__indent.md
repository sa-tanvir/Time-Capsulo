```rust
pub fn indent(s: &str, prefix: &str) -> String {
    let mut result = String::with_capacity(s.len() + prefix.len());
    for line in s.lines() {
        if line.chars().any(|c| !c.is_whitespace()) {
            result.push_str(prefix);
            result.push_str(line);
        }
        result.push('\n');
    }
    result
}
```
