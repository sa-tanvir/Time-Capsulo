pub fn encode<S: Sink>(&self, bytes: &[u8], sink: &mut S) -> Result<(), S::Error> {
    let mut encode_buf: [u8; BUF_SIZE] = [0; BUF_SIZE];
    let encode_table = self.config.char_set.encode_table();

    let mut input_index = 0;

    while input_index < bytes.len() {
        // either the full input chunk size, or it's the last iteration
        let input_chunk_len = cmp::min(self.max_input_chunk_len, bytes.len() - input_index);

        let chunk = &bytes[input_index..(input_index + input_chunk_len)];

        let mut b64_bytes_written = encode_to_slice(chunk, &mut encode_buf, encode_table);

        input_index += input_chunk_len;
        let more_input_left = input_index < bytes.len();

        if self.config.pad && !more_input_left {
            // no more input, add padding if needed. Buffer will have room because
            // max_input_length leaves room for it.
            b64_bytes_written += add_padding(bytes.len(), &mut encode_buf[b64_bytes_written..]);
        }

        sink.write_encoded_bytes(&encode_buf[0..b64_bytes_written])?;
    }

    Ok(())
}
