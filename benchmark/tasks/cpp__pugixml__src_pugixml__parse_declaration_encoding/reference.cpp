PUGI__FN bool parse_declaration_encoding(const uint8_t* data, size_t size, const uint8_t*& out_encoding, size_t& out_length)
{
#define PUGI__SCANCHAR(ch) { if (offset >= size || data[offset] != ch) return false; offset++; }
#define PUGI__SCANCHARTYPE(ct) { while (offset < size && PUGI__IS_CHARTYPE(data[offset], ct)) offset++; }

	// check if we have a non-empty XML declaration
	if (size < 6 || !((data[0] == '<') & (data[1] == '?') & (data[2] == 'x') & (data[3] == 'm') & (data[4] == 'l') && PUGI__IS_CHARTYPE(data[5], ct_space)))
		return false;

	// scan XML declaration until the encoding field
	for (size_t i = 6; i + 1 < size; ++i)
	{
		// declaration can not contain ? in quoted values
		if (data[i] == '?')
			return false;

		if (data[i] == 'e' && data[i + 1] == 'n')
		{
			size_t offset = i;

			// encoding follows the version field which can't contain 'en' so this has to be the encoding if XML is well formed
			PUGI__SCANCHAR('e'); PUGI__SCANCHAR('n'); PUGI__SCANCHAR('c'); PUGI__SCANCHAR('o');
			PUGI__SCANCHAR('d'); PUGI__SCANCHAR('i'); PUGI__SCANCHAR('n'); PUGI__SCANCHAR('g');

			// S? = S?
			PUGI__SCANCHARTYPE(ct_space);
			PUGI__SCANCHAR('=');
			PUGI__SCANCHARTYPE(ct_space);

			// the only two valid delimiters are ' and "
			uint8_t delimiter = (offset < size && data[offset] == '"') ? '"' : '\'';

			PUGI__SCANCHAR(delimiter);

			size_t start = offset;

			out_encoding = data + offset;

			PUGI__SCANCHARTYPE(ct_symbol);

			out_length = offset - start;

			PUGI__SCANCHAR(delimiter);

			return true;
		}
	}

	return false;

#undef PUGI__SCANCHAR
#undef PUGI__SCANCHARTYPE
}
