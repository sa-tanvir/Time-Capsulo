template <typename Traits> static inline typename Traits::value_type process(const uint8_t* data, size_t size, typename Traits::value_type result, Traits)
{
	const uint8_t utf8_byte_mask = 0x3f;

	while (size)
	{
		uint8_t lead = *data;

		// 0xxxxxxx -> U+0000..U+007F
		if (lead < 0x80)
		{
			result = Traits::low(result, lead);
			data += 1;
			size -= 1;

			// process aligned single-byte (ascii) blocks
			if ((reinterpret_cast<uintptr_t>(data) & 3) == 0)
			{
				// round-trip through void* to silence 'cast increases required alignment of target type' warnings
				while (size >= 4 && (*static_cast<const uint32_t*>(static_cast<const void*>(data)) & 0x80808080) == 0)
				{
					result = Traits::low(result, data[0]);
					result = Traits::low(result, data[1]);
					result = Traits::low(result, data[2]);
					result = Traits::low(result, data[3]);
					data += 4;
					size -= 4;
				}
			}
		}
		// 110xxxxx -> U+0080..U+07FF
		else if (static_cast<unsigned int>(lead - 0xC0) < 0x20 && size >= 2 && (data[1] & 0xc0) == 0x80)
		{
			result = Traits::low(result, ((lead & ~0xC0) << 6) | (data[1] & utf8_byte_mask));
			data += 2;
			size -= 2;
		}
		// 1110xxxx -> U+0800-U+FFFF
		else if (static_cast<unsigned int>(lead - 0xE0) < 0x10 && size >= 3 && (data[1] & 0xc0) == 0x80 && (data[2] & 0xc0) == 0x80)
		{
			result = Traits::low(result, ((lead & ~0xE0) << 12) | ((data[1] & utf8_byte_mask) << 6) | (data[2] & utf8_byte_mask));
			data += 3;
			size -= 3;
		}
		// 11110xxx -> U+10000..U+10FFFF
		else if (static_cast<unsigned int>(lead - 0xF0) < 0x08 && size >= 4 && (data[1] & 0xc0) == 0x80 && (data[2] & 0xc0) == 0x80 && (data[3] & 0xc0) == 0x80)
		{
			result = Traits::high(result, ((lead & ~0xF0) << 18) | ((data[1] & utf8_byte_mask) << 12) | ((data[2] & utf8_byte_mask) << 6) | (data[3] & utf8_byte_mask));
			data += 4;
			size -= 4;
		}
		// 10xxxxxx or 11111xxx -> invalid
		else
		{
			data += 1;
			size -= 1;
		}
	}

	return result;
}
