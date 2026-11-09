fn fmt(&self, f: &mut Formatter) -> Result {
    debugln!("OptBuilder::fmt:{}", self.b.name);
    let sep = if self.b.is_set(ArgSettings::RequireEquals) {
        "="
    } else {
        " "
    };
    // Write the name such --long or -l
    if let Some(l) = self.s.long {
        write!(f, "--{}{}", l, sep)?;
    } else {
        write!(f, "-{}{}", self.s.short.unwrap(), sep)?;
    }
    let delim = if self.is_set(ArgSettings::RequireDelimiter) {
        self.v.val_delim.expect(INTERNAL_ERROR_MSG)
    } else {
        ' '
    };

    // Write the values such as <name1> <name2>
    if let Some(ref vec) = self.v.val_names {
        let mut it = vec.iter().peekable();
        while let Some((_, val)) = it.next() {
            write!(f, "<{}>", val)?;
            if it.peek().is_some() {
                write!(f, "{}", delim)?;
            }
        }
        let num = vec.len();
        if self.is_set(ArgSettings::Multiple) && num == 1 {
            write!(f, "...")?;
        }
    } else if let Some(num) = self.v.num_vals {
        let mut it = (0..num).peekable();
        while let Some(_) = it.next() {
            write!(f, "<{}>", self.b.name)?;
            if it.peek().is_some() {
                write!(f, "{}", delim)?;
            }
        }
        if self.is_set(ArgSettings::Multiple) && num == 1 {
            write!(f, "...")?;
        }
    } else {
        write!(
            f,
            "<{}>{}",
            self.b.name,
            if self.is_set(ArgSettings::Multiple) {
                "..."
            } else {
                ""
            }
        )?;
    }

    Ok(())
}
