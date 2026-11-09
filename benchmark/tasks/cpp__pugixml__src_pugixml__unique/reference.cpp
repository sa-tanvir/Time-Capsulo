template <typename I> PUGI__FN I unique(I begin, I end)
{
	// fast skip head
	while (end - begin > 1 && *begin != *(begin + 1))
		begin++;

	if (begin == end)
		return begin;

	// last written element
	I write = begin++;

	// merge unique elements
	while (begin != end)
	{
		if (*begin != *write)
			*++write = *begin++;
		else
			begin++;
	}

	// past-the-end (write points to live element)
	return write + 1;
}
