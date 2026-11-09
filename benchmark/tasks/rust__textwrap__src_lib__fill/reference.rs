pub fn fill(&self, s: &str) -> String {
    // This will avoid reallocation in simple cases (no
    // indentation, no hyphenation).
    let mut result = String::with_capacity(s.len());

    for (i, line) in self.wrap_iter(s).enumerate() {
        if i > 0 {
            result.push('\n');
        }
        result.push_str(&line);
    }

    result
}
