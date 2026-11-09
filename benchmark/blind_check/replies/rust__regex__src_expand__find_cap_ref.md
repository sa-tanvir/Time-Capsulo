```rust
fn find_cap_ref<T: ?Sized + AsRef<[u8]>>(
    replacement: &T,
) -> Option<CaptureRef> {
    let rep: &[u8] = replacement.as_ref();
    if rep.len() <= 1 || rep[0] != b'$' {
        return None;
    }
    let brace = rep[1] == b'{';
    let start = if brace { 2 } else { 1 };
    let mut i = start;
    while i < rep.len() && is_valid_cap_letter(&rep[i]) {
        i += 1;
    }
    if i == start {
        return None;
    }
    let end = if brace {
        if i >= rep.len() || rep[i] != b'}' {
            return None;
        }
        i + 1
    } else {
        i
    };
    // Capture-name bytes are all ASCII, so this never fails.
    let name = match str::from_utf8(&rep[start..i]) {
        Ok(name) => name,
        Err(_) => return None,
    };
    let cap = match name.parse::<u32>() {
        Ok(n) => Ref::Number(n as usize),
        Err(_) => Ref::Named(name),
    };
    Some(CaptureRef { cap: cap, end: end })
}
```
