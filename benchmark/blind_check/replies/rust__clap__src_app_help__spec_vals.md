```rust
fn spec_vals(&self, a: &ArgWithDisplay) -> String {
    let mut spec_vals: Vec<String> = Vec::new();

    if let Some((name, val)) = a.env() {
        if a.is_set(ArgSettings::HideEnvValues) {
            spec_vals.push(format!(" [env: {}]", name.to_string_lossy()));
        } else {
            let v = match val {
                Some(v) => v.to_string_lossy(),
                None => Cow::Borrowed(""),
            };
            spec_vals.push(format!(" [env: {}={}]", name.to_string_lossy(), v));
        }
    }

    if !a.is_set(ArgSettings::HideDefaultValue) {
        if let Some(pv) = a.default_val() {
            let s = pv.to_string_lossy();
            if self.color {
                spec_vals.push(format!(" [default: {}]", self.cizer.good(&*s)));
            } else {
                spec_vals.push(format!(" [default: {}]", s));
            }
        }
    }

    if let Some(aliases) = a.aliases() {
        let joined = if self.color {
            aliases
                .iter()
                .map(|al| format!("{}", self.cizer.good(*al)))
                .collect::<Vec<_>>()
                .join(", ")
        } else {
            aliases.join(", ")
        };
        spec_vals.push(format!(" [aliases: {}]", joined));
    }

    if !self.hide_pv && !a.is_set(ArgSettings::HidePossibleValues) {
        if let Some(pv) = a.possible_vals() {
            let joined = if self.color {
                pv.iter()
                    .map(|v| format!("{}", self.cizer.good(*v)))
                    .collect::<Vec<_>>()
                    .join(", ")
            } else {
                pv.join(", ")
            };
            spec_vals.push(format!(" [possible values: {}]", joined));
        }
    }

    spec_vals.join(" ")
}
```
