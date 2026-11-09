```rust
fn write_args<'b: 'd, 'c: 'd, 'd, I: 'd>(&mut self, args: I) -> io::Result<()>
where
    I: Iterator<Item = &'d ArgWithOrder<'b, 'c>>,
{
    let mut ord_m: BTreeMap<(usize, &'d str), &'d ArgWithOrder<'b, 'c>> = BTreeMap::new();
    let mut longest = 2;
    for arg in args.filter(|arg| {
        !arg.is_set(ArgSettings::Hidden) || arg.is_set(ArgSettings::NextLineHelp)
    }) {
        if arg.longest_filter() {
            longest = cmp::max(longest, str_width(&arg.to_string()));
        }
        ord_m.insert((arg.disp_ord(), arg.name()), arg);
    }
    self.longest = longest;

    let mut first = true;
    for arg in ord_m.values() {
        if first {
            first = false;
        } else {
            self.writer.write_all(b"\n")?;
        }
        self.write_arg(arg.as_base())?;
    }
    Ok(())
}
```
