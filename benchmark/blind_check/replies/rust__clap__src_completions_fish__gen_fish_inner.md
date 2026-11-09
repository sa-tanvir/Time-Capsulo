```rust
fn gen_fish_inner(root_command: &str, comp_gen: &FishGen, parent_cmds: &str, buffer: &mut String) {
    let p = comp_gen.p;
    let basic_template = format!(
        "complete -c {} -n \"__fish_using_command {}\"",
        root_command, parent_cmds
    );

    for option in p.opts() {
        buffer.push_str(&basic_template);
        if let Some(data) = option.s.short {
            buffer.push_str(" -s ");
            buffer.push(data);
        }
        if let Some(data) = option.s.long {
            buffer.push_str(" -l ");
            buffer.push_str(data);
        }
        if let Some(data) = option.b.help {
            buffer.push_str(" -d '");
            buffer.push_str(&escape_string(data));
            buffer.push('\'');
        }
        if let Some(ref data) = option.v.possible_vals {
            buffer.push_str(" -r -f -a \"");
            for (i, v) in data.iter().enumerate() {
                if i > 0 {
                    buffer.push(' ');
                }
                buffer.push_str(v);
            }
            buffer.push('"');
        }
        buffer.push('\n');
    }

    for flag in p.flags() {
        buffer.push_str(&basic_template);
        if let Some(data) = flag.s.short {
            buffer.push_str(" -s ");
            buffer.push(data);
        }
        if let Some(data) = flag.s.long {
            buffer.push_str(" -l ");
            buffer.push_str(data);
        }
        if let Some(data) = flag.b.help {
            buffer.push_str(" -d '");
            buffer.push_str(&escape_string(data));
            buffer.push('\'');
        }
        buffer.push('\n');
    }

    for subcommand in &p.subcommands {
        buffer.push_str(&basic_template);
        buffer.push_str(" -f -a \"");
        buffer.push_str(&subcommand.p.meta.name);
        buffer.push('"');
        if let Some(data) = subcommand.p.meta.about {
            buffer.push_str(" -d '");
            buffer.push_str(&escape_string(data));
            buffer.push('\'');
        }
        buffer.push('\n');
    }

    for subcommand in &p.subcommands {
        let sub_name = &subcommand.p.meta.name;
        let sub_parents = if parent_cmds.is_empty() {
            sub_name.clone()
        } else {
            format!("{} {}", parent_cmds, sub_name)
        };
        let sub_gen = FishGen::new(&subcommand.p);
        gen_fish_inner(root_command, &sub_gen, &sub_parents, buffer);
    }
}
```
