pub fn write_all_args(&mut self, parser: &Parser) -> ClapResult<()> {
    debugln!("Help::write_all_args;");
    let flags = parser.has_flags();
    let pos = parser
        .positionals()
        .filter(|arg| !arg.is_set(ArgSettings::Hidden))
        .count() > 0;
    let opts = parser.has_opts();
    let subcmds = parser.has_visible_subcommands();

    let unified_help = parser.is_set(AppSettings::UnifiedHelpMessage);

    let mut first = true;

    if unified_help && (flags || opts) {
        let opts_flags = parser
            .flags()
            .map(as_arg_trait)
            .chain(parser.opts().map(as_arg_trait));
        color!(self, "OPTIONS:\n", warning)?;
        self.write_args(opts_flags)?;
        first = false;
    } else {
        if flags {
            color!(self, "FLAGS:\n", warning)?;
            self.write_args(parser.flags().map(as_arg_trait))?;
            first = false;
        }
        if opts {
            if !first {
                self.writer.write_all(b"\n\n")?;
            }
            color!(self, "OPTIONS:\n", warning)?;
            self.write_args(parser.opts().map(as_arg_trait))?;
            first = false;
        }
    }

    if pos {
        if !first {
            self.writer.write_all(b"\n\n")?;
        }
        color!(self, "ARGS:\n", warning)?;
        self.write_args_unsorted(parser.positionals().map(as_arg_trait))?;
        first = false;
    }

    if subcmds {
        if !first {
            self.writer.write_all(b"\n\n")?;
        }
        color!(self, "SUBCOMMANDS:\n", warning)?;
        self.write_subcommands(parser)?;
    }

    Ok(())
}
