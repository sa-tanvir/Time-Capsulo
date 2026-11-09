fn write_args<'b: 'd, 'c: 'd, 'd, I: 'd>(&mut self, args: I) -> io::Result<()>
where
    I: Iterator<Item = &'d ArgWithOrder<'b, 'c>>,
{
    debugln!("Help::write_args;");
    // The shortest an arg can legally be is 2 (i.e. '-x')
    self.longest = 2;
    let mut ord_m = VecMap::new();
    // Determine the longest
    for arg in args.filter(|arg| {
        // If it's NextLineHelp, but we don't care to compute how long because it may be
        // NextLineHelp on purpose *because* it's so long and would throw off all other
        // args alignment
        !arg.is_set(ArgSettings::Hidden) || arg.is_set(ArgSettings::NextLineHelp)
    }) {
        if arg.longest_filter() {
            debugln!("Help::write_args: Current Longest...{}", self.longest);
            self.longest = cmp::max(self.longest, str_width(arg.to_string().as_str()));
            debugln!("Help::write_args: New Longest...{}", self.longest);
        }
        let btm = ord_m.entry(arg.disp_ord()).or_insert(BTreeMap::new());
        btm.insert(arg.name(), arg);
    }
    let mut first = true;
    for btm in ord_m.values() {
        for arg in btm.values() {
            if first {
                first = false;
            } else {
                self.writer.write_all(b"\n")?;
            }
            self.write_arg(arg.as_base())?;
        }
    }
    Ok(())
}
