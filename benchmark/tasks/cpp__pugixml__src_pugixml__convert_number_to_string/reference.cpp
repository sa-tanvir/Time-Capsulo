PUGI__FN xpath_string convert_number_to_string(double value, xpath_allocator* alloc)
{
	// try special number conversion
	const char_t* special = convert_number_to_string_special(value);
	if (special) return xpath_string::from_const(special);

	// get mantissa + exponent form
	char mantissa_buffer[32];

	char* mantissa;
	int exponent;
	convert_number_to_mantissa_exponent(value, mantissa_buffer, &mantissa, &exponent);

	// allocate a buffer of suitable length for the number
	size_t result_size = strlen(mantissa_buffer) + (exponent > 0 ? exponent : -exponent) + 4;
	char_t* result = static_cast<char_t*>(alloc->allocate(sizeof(char_t) * result_size));
	if (!result) return xpath_string();

	// make the number!
	char_t* s = result;

	// sign
	if (value < 0) *s++ = '-';

	// integer part
	if (exponent <= 0)
	{
		*s++ = '0';
	}
	else
	{
		while (exponent > 0)
		{
			assert(*mantissa == 0 || static_cast<unsigned int>(*mantissa - '0') <= 9);
			*s++ = *mantissa ? *mantissa++ : '0';
			exponent--;
		}
	}

	// fractional part
	if (*mantissa)
	{
		// decimal point
		*s++ = '.';

		// extra zeroes from negative exponent
		while (exponent < 0)
		{
			*s++ = '0';
			exponent++;
		}

		// extra mantissa digits
		while (*mantissa)
		{
			assert(static_cast<unsigned int>(*mantissa - '0') <= 9);
			*s++ = *mantissa++;
		}
	}

	// zero-terminate
	assert(s < result + result_size);
	*s = 0;

	return xpath_string::from_heap_preallocated(result, s);
}
