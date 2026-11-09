pub fn generic_jaro<'a, 'b, Iter1, Iter2, Elem1, Elem2>(a: &'a Iter1, b: &'b Iter2) -> f64
    where &'a Iter1: IntoIterator<Item=Elem1>,
          &'b Iter2: IntoIterator<Item=Elem2>,
          Elem1: PartialEq<Elem2> {
    panic!("TC_STUB")
}
