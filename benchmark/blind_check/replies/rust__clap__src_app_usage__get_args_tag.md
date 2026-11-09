```rust
fn get_args_tag(p: &Parser, incl_reqs: bool) -> Option<String> {
    use std::collections::HashSet;
    use std::fmt::Write;

    fn eligible(pos: &PosBuilder) -> bool {
        !pos.is_set(ArgSettings::Required)
            && !pos.is_set(ArgSettings::Hidden)
            && !pos.is_set(ArgSettings::Last)
    }

    fn render(out: &mut String, pos: &PosBuilder) {
        let _ = write!(out, " [{}]{}", pos.name_no_brackets(), pos.multiple_str());
    }

    let req_members: HashSet<&str> = p
        .groups
        .iter()
        .filter(|g| g.required)
        .flat_map(|g| g.args.iter().map(|s| *s))
        .collect();

    let count = p
        .positionals
        .values()
        .filter(|pos| eligible(*pos) && !req_members.contains(pos.b.name))
        .take(2)
        .count();

    let dont_collapse = p.is_set(AS::DontCollapseArgsInUsage);

    if !dont_collapse && count > 1 {
        return None;
    }

    if count == 1 && incl_reqs {
        let mut out = String::new();
        if let Some(pos) = p.positionals.values().find(|pos| eligible(*pos)) {
            render(&mut out, pos);
        }
        return Some(out);
    }

    if dont_collapse && !p.positionals.is_empty() && incl_reqs {
        let mut out = String::new();
        for pos in p.positionals.values().filter(|pos| eligible(*pos)) {
            render(&mut out, pos);
        }
        return Some(out);
    }

    if !incl_reqs {
        let highest_req_pos = p
            .positionals
            .iter()
            .filter(|&(_, pos)| {
                pos.is_set(ArgSettings::Required) && !pos.is_set(ArgSettings::Last)
            })
            .map(|(idx, _)| idx)
            .max()
            .unwrap_or_else(|| p.positionals.len());
        let mut out = String::new();
        for (_, pos) in p
            .positionals
            .iter()
            .filter(|&(idx, pos)| idx <= highest_req_pos && eligible(pos))
        {
            render(&mut out, pos);
        }
        return Some(out);
    }

    Some(String::new())
}
```
