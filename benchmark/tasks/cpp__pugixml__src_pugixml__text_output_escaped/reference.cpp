PUGI__FN void text_output_escaped(xml_buffered_writer& writer, const char_t* s, chartypex_t type, unsigned int flags)
{
	while (*s)
	{
		const char_t* prev = s;

		// While *s is a usual symbol
		PUGI__SCANWHILE_UNROLL(!PUGI__IS_CHARTYPEX(ss, type));

		writer.write_buffer(prev, static_cast<size_t>(s - prev));

		switch (*s)
		{
			case 0: break;
			case '&':
				writer.write('&', 'a', 'm', 'p', ';');
				++s;
				break;
			case '<':
				writer.write('&', 'l', 't', ';');
				++s;
				break;
			case '>':
				writer.write('&', 'g', 't', ';');
				++s;
				break;
			case '"':
				if (flags & format_attribute_single_quote)
					writer.write('"');
				else
					writer.write('&', 'q', 'u', 'o', 't', ';');
				++s;
				break;
			case '\'':
				if (flags & format_attribute_single_quote)
					writer.write('&', 'a', 'p', 'o', 's', ';');
				else
					writer.write('\'');
				++s;
				break;
			default: // s is not a usual symbol
			{
				unsigned int ch = static_cast<unsigned int>(*s++);
				assert(ch < 32);

				if (!(flags & format_skip_control_chars))
					writer.write('&', '#', static_cast<char_t>((ch / 10) + '0'), static_cast<char_t>((ch % 10) + '0'), ';');
			}
		}
	}
}
