pub fn osa_distance(a: &str, b: &str) -> usize {
    let a_len = a.chars().count();
    let b_len = b.chars().count();
    if a == b { return 0; }
    else if a_len == 0 { return b_len; }
    else if b_len == 0 { return a_len; }

    let mut prev_two_distances: Vec<usize> = Vec::with_capacity(b_len + 1);
    let mut prev_distances: Vec<usize> = Vec::with_capacity(b_len + 1);
    let mut curr_distances: Vec<usize> = Vec::with_capacity(b_len + 1);

    let mut prev_a_char = char::MAX;
    let mut prev_b_char = char::MAX;

    for i in 0..(b_len + 1) {
        prev_two_distances.push(i);
        prev_distances.push(i);
        curr_distances.push(0);
    }

    for (i, a_char) in a.chars().enumerate() {
        curr_distances[0] = i + 1;

        for (j, b_char) in b.chars().enumerate() {
            let cost = if a_char == b_char { 0 } else { 1 };
            curr_distances[j + 1] = min(curr_distances[j] + 1,
                                        min(prev_distances[j + 1] + 1,
                                            prev_distances[j] + cost));
            if i > 0 && j > 0 && a_char != b_char &&
                a_char == prev_b_char && b_char == prev_a_char {
                curr_distances[j + 1] = min(curr_distances[j + 1],
                                            prev_two_distances[j - 1] + 1);
            }

            prev_b_char = b_char;
        }

        prev_two_distances.clone_from(&prev_distances);
        prev_distances.clone_from(&curr_distances);
        prev_a_char = a_char;
    }

    curr_distances[b_len]

}
