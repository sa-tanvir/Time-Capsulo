```rust
pub fn generic_jaro<'a, 'b, Iter1, Iter2, Elem1, Elem2>(a: &'a Iter1, b: &'b Iter2) -> f64
    where &'a Iter1: IntoIterator<Item=Elem1>,
          &'b Iter2: IntoIterator<Item=Elem2>,
          Elem1: PartialEq<Elem2> {
    let a_len = a.into_iter().count();
    let b_len = b.into_iter().count();

    if a_len == 0 && b_len == 0 {
        return 1.0;
    } else if a_len == 0 || b_len == 0 {
        return 0.0;
    } else if a_len == 1 && b_len == 1 {
        return 0.0;
    }

    let search_range = (max(a_len, b_len) / 2) - 1;

    let mut b_consumed = vec![false; b_len];
    let mut matches = 0.0;
    let mut transpositions = 0.0;
    let mut b_match_index = 0;

    for (i, a_elem) in a.into_iter().enumerate() {
        let min_bound = if i > search_range { i - search_range } else { 0 };
        let max_bound = min(b_len - 1, i + search_range);

        if min_bound > max_bound {
            continue;
        }

        for (j, b_elem) in b
            .into_iter()
            .enumerate()
            .skip(min_bound)
            .take(max_bound - min_bound + 1)
        {
            if !b_consumed[j] && a_elem == b_elem {
                b_consumed[j] = true;
                matches += 1.0;

                if j < b_match_index {
                    transpositions += 1.0;
                }
                b_match_index = j;

                break;
            }
        }
    }

    if matches == 0.0 {
        0.0
    } else {
        (1.0 / 3.0)
            * ((matches / a_len as f64)
                + (matches / b_len as f64)
                + ((matches - transpositions) / matches))
    }
}
```
