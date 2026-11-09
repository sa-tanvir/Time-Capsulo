fn spec_vals(&self, a: &ArgWithDisplay) -> String {
    debugln!("Help::spec_vals: a={}", a);
    let mut spec_vals = vec![];
    if let Some(ref env) = a.env() {
        debugln!(
            "Help::spec_vals: Found environment variable...[{:?}:{:?}]",
            env.0,
            env.1
        );
        let env_val = if !a.is_set(ArgSettings::HideEnvValues) {
            format!("={}", env.1.map_or(Cow::Borrowed(""), |val| val.to_string_lossy()))
        } else {
            String::new()
        };
        let env_info = format!(
            " [env: {}{}]",
            env.0.to_string_lossy(),
            env_val
        );
        spec_vals.push(env_info);
    }
    if !a.is_set(ArgSettings::HideDefaultValue) {
        if let Some(pv) = a.default_val() {
            debugln!("Help::spec_vals: Found default value...[{:?}]", pv);
            spec_vals.push(format!(
                " [default: {}]",
                if self.color {
                    self.cizer.good(pv.to_string_lossy())
                } else {
                    Format::None(pv.to_string_lossy())
                }
            ));
        }
    }
    if let Some(ref aliases) = a.aliases() {
        debugln!("Help::spec_vals: Found aliases...{:?}", aliases);
        spec_vals.push(format!(
            " [aliases: {}]",
            if self.color {
                aliases
                    .iter()
                    .map(|v| format!("{}", self.cizer.good(v)))
                    .collect::<Vec<_>>()
                    .join(", ")
            } else {
                aliases.join(", ")
            }
        ));
    }
    if !self.hide_pv && !a.is_set(ArgSettings::HidePossibleValues) {
        if let Some(pv) = a.possible_vals() {
            debugln!("Help::spec_vals: Found possible vals...{:?}", pv);
            spec_vals.push(if self.color {
                format!(
                    " [possible values: {}]",
                    pv.iter()
                        .map(|v| format!("{}", self.cizer.good(v)))
                        .collect::<Vec<_>>()
                        .join(", ")
                )
            } else {
                format!(" [possible values: {}]", pv.join(", "))
            });
        }
    }
    spec_vals.join(" ")
}
