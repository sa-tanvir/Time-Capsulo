```rust
fn decode_helper(
    input: &[u8],
    num_chunks: usize,
    config: Config,
    output: &mut [u8],
) -> Result<usize, DecodeError> {
    if input.len() % 4 == 1 {
        return Err(DecodeError::InvalidLength);
    }
    if num_chunks == 0 || input.is_empty() {
        return Ok(0);
    }

    let decode_table = config.char_set.decode_table();

    // Start of the final (possibly partial, possibly padded) 8-byte group.
    let last_chunk_start = (num_chunks - 1) * INPUT_CHUNK_LEN;

    let mut input_index = 0;
    let mut output_index = 0;

    if num_chunks >= 2 {
        // Chunks that are followed by another full (non-final) chunk: the 2 filler bytes written
        // by `decode_chunk` are overwritten by the next chunk, so the faster variant is safe.
        let fast_end = (num_chunks - 2) * INPUT_CHUNK_LEN;
        while input_index < fast_end {
            decode_chunk(
                &input[input_index..(input_index + INPUT_CHUNK_LEN)],
                input_index,
                decode_table,
                &mut output[output_index..(output_index + INPUT_CHUNK_LEN)],
            )?;
            input_index += INPUT_CHUNK_LEN;
            output_index += DECODED_CHUNK_LEN;
        }

        // Last full chunk before the final group: write exactly 6 bytes.
        decode_chunk_precise(
            &input[input_index..(input_index + INPUT_CHUNK_LEN)],
            input_index,
            decode_table,
            &mut output[output_index..(output_index + DECODED_CHUNK_LEN)],
        )?;
        input_index += INPUT_CHUNK_LEN;
        output_index += DECODED_CHUNK_LEN;
    }

    debug_assert_eq!(input_index, last_chunk_start);

    // Final group: handle padding and trailing bits.
    let mut leftover_bits: u64 = 0;
    let mut morsels_in_leftover: usize = 0;
    let mut padding_bytes: usize = 0;
    let mut first_padding_index: usize = 0;
    let mut last_symbol: u8 = 0;

    for (i, &b) in input[last_chunk_start..].iter().enumerate() {
        if b == b'=' {
            if i % 4 < 2 {
                // Padding can only appear in the last two positions of a quad.
                let bad_padding_index = last_chunk_start
                    + if padding_bytes > 0 {
                        first_padding_index
                    } else {
                        i
                    };
                return Err(DecodeError::InvalidByte(bad_padding_index, b));
            }
            if padding_bytes == 0 {
                first_padding_index = i;
            }
            padding_bytes += 1;
            continue;
        }

        if padding_bytes > 0 {
            // A symbol after padding.
            return Err(DecodeError::InvalidByte(
                last_chunk_start + first_padding_index,
                b'=',
            ));
        }

        let morsel = decode_table[b as usize];
        if morsel == tables::INVALID_VALUE {
            return Err(DecodeError::InvalidByte(last_chunk_start + i, b));
        }

        last_symbol = b;
        let shift = 64 - (morsels_in_leftover + 1) * 6;
        leftover_bits |= (morsel as u64) << shift;
        morsels_in_leftover += 1;
    }

    let leftover_bytes = morsels_in_leftover * 6 / 8;

    if leftover_bytes < 8 && !config.decode_allow_trailing_bits && morsels_in_leftover > 0 {
        let mask = !0u64 >> (leftover_bytes * 8);
        if leftover_bits & mask != 0 {
            return Err(DecodeError::InvalidLastSymbol(
                last_chunk_start + morsels_in_leftover - 1,
                last_symbol,
            ));
        }
    }

    for k in 0..leftover_bytes {
        output[output_index + k] = (leftover_bits >> (56 - k * 8)) as u8;
    }

    Ok(output_index + leftover_bytes)
}
```
