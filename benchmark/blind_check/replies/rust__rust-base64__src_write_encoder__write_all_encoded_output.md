```rust
fn write_all_encoded_output(&mut self) -> Result<()> {
    while self.output_occupied_len > 0 {
        let remaining_len = self.output_occupied_len;
        match self.write_to_delegate(remaining_len) {
            Ok(_) => {}
            Err(ref e) if e.kind() == ErrorKind::Interrupted => {}
            Err(e) => return Err(e),
        }
    }

    Ok(())
}
```
