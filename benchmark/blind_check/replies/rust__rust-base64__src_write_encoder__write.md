```rust
fn write(&mut self, input: &[u8]) -> Result<usize> {
    if self.finished {
        panic!("Cannot write more after calling finish()");
    }

    if input.is_empty() {
        return Ok(0);
    }

    // Pending encoded output from a previous call: try to flush it, consume no input.
    if self.output_occupied_len > 0 {
        let current_len = self.output_occupied_len;
        return self.write_to_delegate(current_len).map(|_| 0);
    }

    let orig_extra_len = self.extra_input_occupied_len;
    let mut input = input;
    let mut extra_input_read_len = 0;
    let mut encoded_size = 0;
    let mut max_input_len = MAX_INPUT_LEN;

    if self.extra_input_occupied_len > 0 {
        if input.len() + self.extra_input_occupied_len < MIN_ENCODE_CHUNK_SIZE {
            // Still not enough for a full group: just buffer the byte.
            self.extra_input[self.extra_input_occupied_len] = input[0];
            self.extra_input_occupied_len += 1;
            return Ok(1);
        }

        extra_input_read_len = MIN_ENCODE_CHUNK_SIZE - self.extra_input_occupied_len;
        self.extra_input[self.extra_input_occupied_len..MIN_ENCODE_CHUNK_SIZE]
            .copy_from_slice(&input[0..extra_input_read_len]);

        encoded_size += encode_to_slice(
            &self.extra_input[0..MIN_ENCODE_CHUNK_SIZE],
            &mut self.output[..],
            self.config.char_set.encode_table(),
        );
        self.extra_input_occupied_len = 0;

        input = &input[extra_input_read_len..];
        max_input_len = MAX_INPUT_LEN - MIN_ENCODE_CHUNK_SIZE;
    } else if input.len() < MIN_ENCODE_CHUNK_SIZE {
        self.extra_input[0..input.len()].copy_from_slice(input);
        self.extra_input_occupied_len = input.len();
        return Ok(input.len());
    }

    let complete_chunks_len = input.len() - (input.len() % MIN_ENCODE_CHUNK_SIZE);
    let input_chunks_to_encode_len = cmp::min(complete_chunks_len, max_input_len);

    encoded_size += encode_to_slice(
        &input[0..input_chunks_to_encode_len],
        &mut self.output[encoded_size..],
        self.config.char_set.encode_table(),
    );

    match self.write_to_delegate(encoded_size) {
        Ok(_) => Ok(extra_input_read_len + input_chunks_to_encode_len),
        Err(e) => {
            // Behave as if nothing happened so the caller can retry with the same input.
            self.extra_input_occupied_len = orig_extra_len;
            Err(e)
        }
    }
}
```
