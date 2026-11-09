pub fn replacen<'t, R: Replacer>(
    &self,
    text: &'t str,
    limit: usize,
    mut rep: R,
) -> Cow<'t, str> {
    // TODO: implement according to the specification
}
