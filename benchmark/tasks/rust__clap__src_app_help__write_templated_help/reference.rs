fn write_templated_help(&mut self, parser: &Parser, template: &str) -> ClapResult<()> {
    debugln!("Help::write_templated_help;");
    let mut tmplr = Cursor::new(&template);
    let mut tag_buf = Cursor::new(vec![0u8; 15]);

    // The strategy is to copy the template from the the reader to wrapped stream
    // until a tag is found. Depending on its value, the appropriate content is copied
    // to the wrapped stream.
    // The copy from template is then resumed, repeating this sequence until reading
    // the complete template.

    loop {
        let tag_length = match copy_and_capture(&mut tmplr, &mut self.writer, &mut tag_buf) {
            None => return Ok(()),
            Some(Err(e)) => return Err(Error::from(e)),
            Some(Ok(val)) if val > 0 => val,
            _ => continue,
        };

        debugln!("Help::write_template_help:iter: tag_buf={};", unsafe {
            String::from_utf8_unchecked(
                tag_buf.get_ref()[0..tag_length]
                    .iter()
                    .map(|&i| i)
                    .collect::<Vec<_>>(),
            )
        });
        match &tag_buf.get_ref()[0..tag_length] {
            b"?" => {
                self.writer.write_all(b"Could not decode tag name")?;
            }
            b"bin" => {
                self.write_bin_name(parser)?;
            }
            b"version" => {
                write!(
                    self.writer,
                    "{}",
                    parser.meta.version.unwrap_or("unknown version")
                )?;
            }
            b"author" => {
                write!(
                    self.writer,
                    "{}",
                    parser.meta.author.unwrap_or("unknown author")
                )?;
            }
            b"about" => {
                write!(
                    self.writer,
                    "{}",
                    parser.meta.about.unwrap_or("unknown about")
                )?;
            }
            b"long-about" => {
                write!(
                    self.writer,
                    "{}",
                    parser.meta.long_about.unwrap_or("unknown about")
                )?;
            }
            b"usage" => {
                write!(self.writer, "{}", usage::create_usage_no_title(parser, &[]))?;
            }
            b"all-args" => {
                self.write_all_args(parser)?;
            }
            b"unified" => {
                let opts_flags = parser
                    .flags()
                    .map(as_arg_trait)
                    .chain(parser.opts().map(as_arg_trait));
                self.write_args(opts_flags)?;
            }
            b"flags" => {
                self.write_args(parser.flags().map(as_arg_trait))?;
            }
            b"options" => {
                self.write_args(parser.opts().map(as_arg_trait))?;
            }
            b"positionals" => {
                self.write_args(parser.positionals().map(as_arg_trait))?;
            }
            b"subcommands" => {
                self.write_subcommands(parser)?;
            }
            b"after-help" => {
                write!(
                    self.writer,
                    "{}",
                    parser.meta.more_help.unwrap_or("unknown after-help")
                )?;
            }
            b"before-help" => {
                write!(
                    self.writer,
                    "{}",
                    parser.meta.pre_help.unwrap_or("unknown before-help")
                )?;
            }
            // Unknown tag, write it back.
            r => {
                self.writer.write_all(b"{")?;
                self.writer.write_all(r)?;
                self.writer.write_all(b"}")?;
            }
        }
    }
}
