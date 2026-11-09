```rust
fn help<'b, 'c>(&mut self, arg: &ArgWithDisplay<'b, 'c>, spec_vals: &str) -> io::Result<()> {
    let h = if self.use_long {
        arg.long_help().unwrap_or_else(|| arg.help().unwrap_or(""))
    } else {
        arg.help().unwrap_or_else(|| arg.long_help().unwrap_or(""))
    };
    let mut help = String::with_capacity(h.len() + spec_vals.len());
    help.push_str(h);
    help.push_str(spec_vals);

    let nlh = self.next_line_help || arg.is_set(ArgSettings::NextLineHelp) || self.use_long;
    let next_line = nlh || self.force_next_line;
    let spcs = if next_line { 12 } else { self.longest + 12 };
    let too_long = spcs + str_width(h) + str_width(spec_vals) >= self.term_w;

    if next_line {
        write!(self.writer, "\n{}{}{}", TAB, TAB, TAB)?;
    }

    if (too_long && spcs <= self.term_w) || h.contains("{n}") {
        help = wrap_help(&help.replace("{n}", "\n"), self.term_w.saturating_sub(spcs));
    }

    {
        let mut lines = help.lines();
        if let Some(first) = lines.next() {
            write!(self.writer, "{}", first)?;
        }
        for part in lines {
            self.writer.write_all(b"\n")?;
            if next_line {
                write!(self.writer, "{}{}{}", TAB, TAB, TAB)?;
            } else if arg.has_switch() {
                write_nspaces!(self.writer, self.longest + 12);
            } else {
                write_nspaces!(self.writer, self.longest + 8);
            }
            write!(self.writer, "{}", part)?;
        }
    }

    if !help.contains('\n') && next_line {
        self.writer.write_all(b"\n")?;
    }
    Ok(())
}
```
