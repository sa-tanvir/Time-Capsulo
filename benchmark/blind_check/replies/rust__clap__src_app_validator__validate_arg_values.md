```rust
fn validate_arg_values<A>(
    &self,
    arg: &A,
    ma: &MatchedArg,
    matcher: &ArgMatcher<'a>,
) -> ClapResult<()>
where
    A: AnyArg<'a, 'b> + Display,
{
    let strict_utf8 = self.0.is_set(AS::StrictUtf8);
    let possible_vals = arg.possible_vals();
    let case_insensitive = arg.is_set(ArgSettings::CaseInsensitive);
    let empty_ok = arg.is_set(ArgSettings::EmptyValues);
    let validator = arg.validator();
    let validator_os = arg.validator_os();

    for val in &ma.vals {
        if strict_utf8 && val.to_str().is_none() {
            return Err(Error::invalid_utf8(
                usage::create_error_usage(&*self.0, matcher, None),
                self.0.color(),
            ));
        }
        if let Some(p_vals) = possible_vals {
            let val_str = val.to_string_lossy();
            let ok = if case_insensitive {
                p_vals
                    .iter()
                    .any(|pv| pv.eq_ignore_ascii_case(&*val_str))
            } else {
                p_vals.iter().any(|pv| *pv == &*val_str)
            };
            if !ok {
                return Err(Error::invalid_value(
                    &*val_str,
                    p_vals,
                    arg,
                    usage::create_error_usage(&*self.0, matcher, None),
                    self.0.color(),
                ));
            }
        }
        if !empty_ok && val.is_empty_() && matcher.contains(arg.name()) {
            return Err(Error::empty_value(
                arg,
                usage::create_error_usage(&*self.0, matcher, None),
                self.0.color(),
            ));
        }
        if let Some(vtor) = validator {
            if let Err(e) = vtor(val.to_string_lossy().into_owned()) {
                return Err(Error::value_validation(Some(arg), e, self.0.color()));
            }
        }
        if let Some(vtor) = validator_os {
            if let Err(e) = vtor(val) {
                return Err(Error::value_validation(
                    Some(arg),
                    e.to_string_lossy().into_owned(),
                    self.0.color(),
                ));
            }
        }
    }
    Ok(())
}
```
