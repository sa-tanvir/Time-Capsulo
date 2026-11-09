fn validate_arg_values<A>(
    &self,
    arg: &A,
    ma: &MatchedArg,
    matcher: &ArgMatcher<'a>,
) -> ClapResult<()>
where
    A: AnyArg<'a, 'b> + Display,
{
    debugln!("Validator::validate_arg_values: arg={:?}", arg.name());
    for val in &ma.vals {
        if self.0.is_set(AS::StrictUtf8) && val.to_str().is_none() {
            debugln!(
                "Validator::validate_arg_values: invalid UTF-8 found in val {:?}",
                val
            );
            return Err(Error::invalid_utf8(
                &*usage::create_error_usage(self.0, matcher, None),
                self.0.color(),
            ));
        }
        if let Some(p_vals) = arg.possible_vals() {
            debugln!("Validator::validate_arg_values: possible_vals={:?}", p_vals);
            let val_str = val.to_string_lossy();
            let ok = if arg.is_set(ArgSettings::CaseInsensitive) {
                p_vals.iter().any(|pv| pv.eq_ignore_ascii_case(&*val_str))
            } else {
                p_vals.contains(&&*val_str)
            };
            if !ok {
                return Err(Error::invalid_value(
                    val_str,
                    p_vals,
                    arg,
                    &*usage::create_error_usage(self.0, matcher, None),
                    self.0.color(),
                ));
            }
        }
        if !arg.is_set(ArgSettings::EmptyValues) && val.is_empty_()
            && matcher.contains(&*arg.name())
        {
            debugln!("Validator::validate_arg_values: illegal empty val found");
            return Err(Error::empty_value(
                arg,
                &*usage::create_error_usage(self.0, matcher, None),
                self.0.color(),
            ));
        }
        if let Some(vtor) = arg.validator() {
            debug!("Validator::validate_arg_values: checking validator...");
            if let Err(e) = vtor(val.to_string_lossy().into_owned()) {
                sdebugln!("error");
                return Err(Error::value_validation(Some(arg), e, self.0.color()));
            } else {
                sdebugln!("good");
            }
        }
        if let Some(vtor) = arg.validator_os() {
            debug!("Validator::validate_arg_values: checking validator_os...");
            if let Err(e) = vtor(val) {
                sdebugln!("error");
                return Err(Error::value_validation(
                    Some(arg),
                    (*e).to_string_lossy().to_string(),
                    self.0.color(),
                ));
            } else {
                sdebugln!("good");
            }
        }
    }
    Ok(())
}
