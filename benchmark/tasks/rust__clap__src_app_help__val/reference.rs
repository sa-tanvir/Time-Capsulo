fn val<'b, 'c>(&mut self, arg: &ArgWithDisplay<'b, 'c>) -> Result<String, io::Error> {
    debugln!("Help::val: arg={}", arg);
    if arg.takes_value() {
        let delim = if arg.is_set(ArgSettings::RequireDelimiter) {
            arg.val_delim().expect(INTERNAL_ERROR_MSG)
        } else {
            ' '
        };
        if let Some(vec) = arg.val_names() {
            let mut it = vec.iter().peekable();
            while let Some((_, val)) = it.next() {
                color!(self, "<{}>", val, good)?;
                if it.peek().is_some() {
                    write!(self.writer, "{}", delim)?;
                }
            }
            let num = vec.len();
            if arg.is_set(ArgSettings::Multiple) && num == 1 {
                color!(self, "...", good)?;
            }
        } else if let Some(num) = arg.num_vals() {
            let mut it = (0..num).peekable();
            while let Some(_) = it.next() {
                color!(self, "<{}>", arg.name(), good)?;
                if it.peek().is_some() {
                    write!(self.writer, "{}", delim)?;
                }
            }
            if arg.is_set(ArgSettings::Multiple) && num == 1 {
                color!(self, "...", good)?;
            }
        } else if arg.has_switch() {
            color!(self, "<{}>", arg.name(), good)?;
            if arg.is_set(ArgSettings::Multiple) {
                color!(self, "...", good)?;
            }
        } else {
            color!(self, "{}", arg, good)?;
        }
    }

    let spec_vals = self.spec_vals(arg);
    let h = arg.help().unwrap_or("");
    let h_w = str_width(h) + str_width(&*spec_vals);
    let nlh = self.next_line_help || arg.is_set(ArgSettings::NextLineHelp);
    let taken = self.longest + 12;
    self.force_next_line = !nlh && self.term_w >= taken
        && (taken as f32 / self.term_w as f32) > 0.40
        && h_w > (self.term_w - taken);

    debug!("Help::val: Has switch...");
    if arg.has_switch() {
        sdebugln!("Yes");
        debugln!("Help::val: force_next_line...{:?}", self.force_next_line);
        debugln!("Help::val: nlh...{:?}", nlh);
        debugln!("Help::val: taken...{}", taken);
        debugln!(
            "Help::val: help_width > (width - taken)...{} > ({} - {})",
            h_w,
            self.term_w,
            taken
        );
        debugln!("Help::val: longest...{}", self.longest);
        debug!("Help::val: next_line...");
        if !(nlh || self.force_next_line) {
            sdebugln!("No");
            let self_len = str_width(arg.to_string().as_str());
            // subtract ourself
            let mut spcs = self.longest - self_len;
            // Since we're writing spaces from the tab point we first need to know if we
            // had a long and short, or just short
            if arg.long().is_some() {
                // Only account 4 after the val
                spcs += 4;
            } else {
                // Only account for ', --' + 4 after the val
                spcs += 8;
            }

            write_nspaces!(self.writer, spcs);
        } else {
            sdebugln!("Yes");
        }
    } else if !(nlh || self.force_next_line) {
        sdebugln!("No, and not next_line");
        write_nspaces!(
            self.writer,
            self.longest + 4 - (str_width(arg.to_string().as_str()))
        );
    } else {
        sdebugln!("No");
    }
    Ok(spec_vals)
}
