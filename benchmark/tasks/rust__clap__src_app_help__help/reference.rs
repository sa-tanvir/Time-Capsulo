fn help<'b, 'c>(&mut self, arg: &ArgWithDisplay<'b, 'c>, spec_vals: &str) -> io::Result<()> {
    debugln!("Help::help;");
    let h = if self.use_long {
        arg.long_help().unwrap_or_else(|| arg.help().unwrap_or(""))
    } else {
        arg.help().unwrap_or_else(|| arg.long_help().unwrap_or(""))
    };
    let mut help = String::from(h) + spec_vals;
    let nlh = self.next_line_help || arg.is_set(ArgSettings::NextLineHelp) || self.use_long;
    debugln!("Help::help: Next Line...{:?}", nlh);

    let spcs = if nlh || self.force_next_line {
        12 // "tab" * 3
    } else {
        self.longest + 12
    };

    let too_long = spcs + str_width(h) + str_width(&*spec_vals) >= self.term_w;

    // Is help on next line, if so then indent
    if nlh || self.force_next_line {
        write!(self.writer, "\n{}{}{}", TAB, TAB, TAB)?;
    }

    debug!("Help::help: Too long...");
    if too_long && spcs <= self.term_w || h.contains("{n}") {
        sdebugln!("Yes");
        debugln!("Help::help: help...{}", help);
        debugln!("Help::help: help width...{}", str_width(&*help));
        // Determine how many newlines we need to insert
        let avail_chars = self.term_w - spcs;
        debugln!("Help::help: Usable space...{}", avail_chars);
        help = wrap_help(&help.replace("{n}", "\n"), avail_chars);
    } else {
        sdebugln!("No");
    }
    if let Some(part) = help.lines().next() {
        write!(self.writer, "{}", part)?;
    }
    for part in help.lines().skip(1) {
        write!(self.writer, "\n")?;
        if nlh || self.force_next_line {
            write!(self.writer, "{}{}{}", TAB, TAB, TAB)?;
        } else if arg.has_switch() {
            write_nspaces!(self.writer, self.longest + 12);
        } else {
            write_nspaces!(self.writer, self.longest + 8);
        }
        write!(self.writer, "{}", part)?;
    }
    if !help.contains('\n') && (nlh || self.force_next_line) {
        write!(self.writer, "\n")?;
    }
    Ok(())
}
