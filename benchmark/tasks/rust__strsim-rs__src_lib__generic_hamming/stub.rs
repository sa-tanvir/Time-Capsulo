pub fn generic_hamming<Iter1, Iter2, Elem1, Elem2>(a: Iter1, b: Iter2) -> HammingResult
    where Iter1: IntoIterator<Item=Elem1>,
          Iter2: IntoIterator<Item=Elem2>,
          Elem1: PartialEq<Elem2> {
    // TODO: implement according to the specification
}
