```rust
pub fn osa_distance(a: &str, b: &str) -> usize {
    let a_chars: Vec<char> = a.chars().collect();
    let b_chars: Vec<char> = b.chars().collect();
    let a_len = a_chars.len();
    let b_len = b_chars.len();

    if a_len == 0 {
        return b_len;
    }
    if b_len == 0 {
        return a_len;
    }

    // Three rolling rows of the DP matrix: i-2, i-1 and i.
    let mut prev_two_distances: Vec<usize> = (0..b_len + 1).collect();
    let mut prev_distances: Vec<usize> = (0..b_len + 1).collect();
    let mut curr_distances: Vec<usize> = vec![0; b_len + 1];

    for i in 0..a_len {
        curr_distances[0] = i + 1;

        for j in 0..b_len {
            let cost = if a_chars[i] == b_chars[j] { 0 } else { 1 };

            let mut d = min(
                curr_distances[j] + 1,
                min(prev_distances[j + 1] + 1, prev_distances[j] + cost),
            );

            if i > 0
                && j > 0
                && a_chars[i] != b_chars[j]
                && a_chars[i] == b_chars[j - 1]
                && a_chars[i - 1] == b_chars[j]
            {
                d = min(d, prev_two_distances[j - 1] + 1);
            }

            curr_distances[j + 1] = d;
        }

        std::mem::swap(&mut prev_two_distances, &mut prev_distances);
        std::mem::swap(&mut prev_distances, &mut curr_distances);
    }

    prev_distances[b_len]
}
```
