fn validate_arg_values<A>(
    &self,
    arg: &A,
    ma: &MatchedArg,
    matcher: &ArgMatcher<'a>,
) -> ClapResult<()>
where
    A: AnyArg<'a, 'b> + Display,
{
    panic!("TC_STUB")
}
