fn write_args<'b: 'd, 'c: 'd, 'd, I: 'd>(&mut self, args: I) -> io::Result<()>
where
    I: Iterator<Item = &'d ArgWithOrder<'b, 'c>>,
{
    // TODO: implement according to the specification
}
