```rust
pub fn dedent(s: &str) -> String {
    let mut prefix = "";
    let mut lines = s.lines();

    // The first non-blank line determines the initial prefix.
    for line in &mut lines {
        let mut whitespace_idx = line.len();
        for (idx, ch) in line.char_indices() {
            if !ch.is_whitespace() {
                whitespace_idx = idx;
                break;
            }
        }

        if whitespace_idx < line.len() {
            prefix = &line[..whitespace_idx];
            break;
        }
    }

    // Every subsequent line can shorten the prefix.
    for line in &mut lines {
        if prefix.is_empty() {
            break;
        }
        for ((idx, a), b) in line.char_indices().zip(prefix.chars()) {
            if a != b {
                prefix = &prefix[..idx];
                break;
            }
        }
    }

    let mut result = String::with_capacity(s.len());
    for line in s.lines() {
        if line.starts_with(prefix) && line.chars().any(|c| !c.is_whitespace()) {
            let (_, tail) = line.split_at(prefix.len());
            result.push_str(tail);
        }
        result.push('\n');
    }

    if result.ends_with('\n') && !s.ends_with('\n') {
        let new_len = result.len() - 1;
        result.truncate(new_len);
    }

    result
}
```
