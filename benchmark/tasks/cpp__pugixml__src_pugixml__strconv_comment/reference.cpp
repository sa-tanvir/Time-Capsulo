PUGI__FN char_t* strconv_comment(char_t* s, char_t endch)
{
	gap g;

	while (true)
	{
		PUGI__SCANWHILE_UNROLL(!PUGI__IS_CHARTYPE(ss, ct_parse_comment));

		if (*s == '\r') // Either a single 0x0d or 0x0d 0x0a pair
		{
			*s++ = '\n'; // replace first one with 0x0a

			if (*s == '\n') g.push(s, 1);
		}
		else if (s[0] == '-' && s[1] == '-' && PUGI__ENDSWITH(s[2], '>')) // comment ends here
		{
			*g.flush(s) = 0;

			return s + (s[2] == '>' ? 3 : 2);
		}
		else if (*s == 0)
		{
			return 0;
		}
		else ++s;
	}
}
