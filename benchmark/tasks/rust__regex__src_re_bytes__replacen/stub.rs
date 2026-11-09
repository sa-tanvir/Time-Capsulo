pub fn replacen<'t, R: Replacer>(
    &self,
    text: &'t [u8],
    limit: usize,
    mut rep: R,
) -> Cow<'t, [u8]> {
    // TODO: implement according to the specification
}
