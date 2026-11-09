template <typename U> PUGI__FN PUGI__UNSIGNED_OVERFLOW U string_to_integer(const char_t* value, U minv, U maxv)
{
	U result = 0;
	const char_t* s = value;

	while (PUGI__IS_CHARTYPE(*s, ct_space))
		s++;

	bool negative = (*s == '-');

	s += (*s == '+' || *s == '-');

	bool overflow = false;

	if (s[0] == '0' && (s[1] | ' ') == 'x')
	{
		s += 2;

		// since overflow detection relies on length of the sequence skip leading zeros
		while (*s == '0')
			s++;

		const char_t* start = s;

		for (;;)
		{
			if (static_cast<unsigned>(*s - '0') < 10)
				result = result * 16 + (*s - '0');
			else if (static_cast<unsigned>((*s | ' ') - 'a') < 6)
				result = result * 16 + ((*s | ' ') - 'a' + 10);
			else
				break;

			s++;
		}

		size_t digits = static_cast<size_t>(s - start);

		overflow = digits > sizeof(U) * 2;
	}
	else
	{
		// since overflow detection relies on length of the sequence skip leading zeros
		while (*s == '0')
			s++;

		const char_t* start = s;

		for (;;)
		{
			if (static_cast<unsigned>(*s - '0') < 10)
				result = result * 10 + (*s - '0');
			else
				break;

			s++;
		}

		size_t digits = static_cast<size_t>(s - start);

		PUGI__STATIC_ASSERT(sizeof(U) == 8 || sizeof(U) == 4 || sizeof(U) == 2);

		const size_t max_digits10 = sizeof(U) == 8 ? 20 : sizeof(U) == 4 ? 10 : 5;
		const char_t max_lead = sizeof(U) == 8 ? '1' : sizeof(U) == 4 ? '4' : '6';
		const size_t high_bit = sizeof(U) * 8 - 1;

		overflow = digits >= max_digits10 && !(digits == max_digits10 && (*start < max_lead || (*start == max_lead && result >> high_bit)));
	}

	if (negative)
	{
		// Workaround for crayc++ CC-3059: Expected no overflow in routine.
	#ifdef _CRAYC
		return (overflow || result > ~minv + 1) ? minv : ~result + 1;
	#else
		return (overflow || result > 0 - minv) ? minv : 0 - result;
	#endif
	}
	else
		return (overflow || result > maxv) ? maxv : result;
}
