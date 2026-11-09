template <typename I, typename Pred> PUGI__FN void sort(I begin, I end, const Pred& pred)
{
	// sort large chunks
	while (end - begin > 16)
	{
		// find median element
		I middle = begin + (end - begin) / 2;
		I median = median3(begin, middle, end - 1, pred);

		// partition in three chunks (< = >)
		I eqbeg, eqend;
		partition3(begin, end, *median, pred, &eqbeg, &eqend);

		// loop on larger half
		if (eqbeg - begin > end - eqend)
		{
			sort(eqend, end, pred);
			end = eqbeg;
		}
		else
		{
			sort(begin, eqbeg, pred);
			begin = eqend;
		}
	}

	// insertion sort small chunk
	insertion_sort(begin, end, pred);
}
