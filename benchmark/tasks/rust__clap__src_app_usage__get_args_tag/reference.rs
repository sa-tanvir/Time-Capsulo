fn get_args_tag(p: &Parser, incl_reqs: bool) -> Option<String> {
    debugln!("usage::get_args_tag;");
    let mut count = 0;
    'outer: for pos in p.positionals
        .values()
        .filter(|pos| !pos.is_set(ArgSettings::Required))
        .filter(|pos| !pos.is_set(ArgSettings::Hidden))
        .filter(|pos| !pos.is_set(ArgSettings::Last))
    {
        debugln!("usage::get_args_tag:iter:{}:", pos.b.name);
        if let Some(g_vec) = p.groups_for_arg(pos.b.name) {
            for grp_s in &g_vec {
                debugln!("usage::get_args_tag:iter:{}:iter:{};", pos.b.name, grp_s);
                // if it's part of a required group we don't want to count it
                if p.groups.iter().any(|g| g.required && (&g.name == grp_s)) {
                    continue 'outer;
                }
            }
        }
        count += 1;
        debugln!(
            "usage::get_args_tag:iter: {} Args not required or hidden",
            count
        );
    }
    if !p.is_set(AS::DontCollapseArgsInUsage) && count > 1 {
        debugln!("usage::get_args_tag:iter: More than one, returning [ARGS]");
        return None; // [ARGS]
    } else if count == 1 && incl_reqs {
        let pos = p.positionals
            .values()
            .find(|pos| {
                !pos.is_set(ArgSettings::Required) && !pos.is_set(ArgSettings::Hidden)
                    && !pos.is_set(ArgSettings::Last)
            })
            .expect(INTERNAL_ERROR_MSG);
        debugln!(
            "usage::get_args_tag:iter: Exactly one, returning '{}'",
            pos.name()
        );
        return Some(format!(
            " [{}]{}",
            pos.name_no_brackets(),
            pos.multiple_str()
        ));
    } else if p.is_set(AS::DontCollapseArgsInUsage) && !p.positionals.is_empty() && incl_reqs {
        debugln!("usage::get_args_tag:iter: Don't collapse returning all");
        return Some(
            p.positionals
                .values()
                .filter(|pos| !pos.is_set(ArgSettings::Required))
                .filter(|pos| !pos.is_set(ArgSettings::Hidden))
                .filter(|pos| !pos.is_set(ArgSettings::Last))
                .map(|pos| {
                    format!(" [{}]{}", pos.name_no_brackets(), pos.multiple_str())
                })
                .collect::<Vec<_>>()
                .join(""),
        );
    } else if !incl_reqs {
        debugln!("usage::get_args_tag:iter: incl_reqs=false, building secondary usage string");
        let highest_req_pos = p.positionals
            .iter()
            .filter_map(|(idx, pos)| {
                if pos.b.is_set(ArgSettings::Required) && !pos.b.is_set(ArgSettings::Last) {
                    Some(idx)
                } else {
                    None
                }
            })
            .max()
            .unwrap_or_else(|| p.positionals.len());
        return Some(
            p.positionals
                .iter()
                .filter_map(|(idx, pos)| {
                    if idx <= highest_req_pos {
                        Some(pos)
                    } else {
                        None
                    }
                })
                .filter(|pos| !pos.is_set(ArgSettings::Required))
                .filter(|pos| !pos.is_set(ArgSettings::Hidden))
                .filter(|pos| !pos.is_set(ArgSettings::Last))
                .map(|pos| {
                    format!(" [{}]{}", pos.name_no_brackets(), pos.multiple_str())
                })
                .collect::<Vec<_>>()
                .join(""),
        );
    }
    Some("".into())
}
