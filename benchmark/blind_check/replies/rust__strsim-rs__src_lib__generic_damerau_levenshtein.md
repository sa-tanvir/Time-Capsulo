```rust
pub fn generic_damerau_levenshtein<Elem>(a_elems: &[Elem], b_elems: &[Elem]) -> usize
    where Elem: Eq + Hash + Clone {
    let a_len = a_elems.len();
    let b_len = b_elems.len();

    if a_len == 0 {
        return b_len;
    }
    if b_len == 0 {
        return a_len;
    }

    // (a_len + 2) x (b_len + 2) matrix, row-major, row = index into a, column = index into b.
    let width = b_len + 2;
    let mut distances = vec![0usize; (a_len + 2) * width];
    let max_distance = a_len + b_len;
    distances[0] = max_distance;

    for i in 0..(a_len + 1) {
        distances[(i + 1) * width] = max_distance;
        distances[(i + 1) * width + 1] = i;
    }

    for j in 0..(b_len + 1) {
        distances[j + 1] = max_distance;
        distances[width + j + 1] = j;
    }

    // Last row (1-based) in which each element of `a` was seen.
    let mut elems: HashMap<Elem, usize> = HashMap::with_capacity(64);

    for i in 1..(a_len + 1) {
        let mut db = 0;

        for j in 1..(b_len + 1) {
            let k = match elems.get(&b_elems[j - 1]) {
                Some(&value) => value,
                None => 0,
            };

            let l = db;

            let cost = if a_elems[i - 1] == b_elems[j - 1] {
                db = j;
                0
            } else {
                1
            };

            let substitution_cost = distances[i * width + j] + cost;
            let insertion_cost = distances[i * width + j + 1] + 1;
            let deletion_cost = distances[(i + 1) * width + j] + 1;
            let transposition_cost =
                distances[k * width + l] + (i - k - 1) + 1 + (j - l - 1);

            distances[(i + 1) * width + j + 1] = min(
                substitution_cost,
                min(insertion_cost, min(deletion_cost, transposition_cost)),
            );
        }

        elems.insert(a_elems[i - 1].clone(), i);
    }

    distances[(a_len + 1) * width + b_len + 1]
}
```
