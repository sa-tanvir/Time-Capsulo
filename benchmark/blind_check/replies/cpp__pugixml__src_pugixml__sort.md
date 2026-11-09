```cpp
template <typename I, typename Pred> PUGI__FN void sort(I begin, I end, const Pred& pred)
{
    ptrdiff_t n = end - begin;

    int depth = 0;
    for (ptrdiff_t m = n; m > 1; m >>= 1) depth += 2;

    while (n > 16)
    {
        if (depth-- <= 0)
        {
            // heap sort fallback
            for (ptrdiff_t start = n / 2; start > 0; --start)
            {
                ptrdiff_t root = start - 1;
                for (;;)
                {
                    ptrdiff_t child = 2 * root + 1;
                    if (child >= n) break;
                    if (child + 1 < n && pred(*(begin + child), *(begin + child + 1))) ++child;
                    if (!pred(*(begin + root), *(begin + child))) break;
                    swap(*(begin + root), *(begin + child));
                    root = child;
                }
            }

            for (ptrdiff_t last = n - 1; last > 0; --last)
            {
                swap(*begin, *(begin + last));

                ptrdiff_t root = 0;
                for (;;)
                {
                    ptrdiff_t child = 2 * root + 1;
                    if (child >= last) break;
                    if (child + 1 < last && pred(*(begin + child), *(begin + child + 1))) ++child;
                    if (!pred(*(begin + root), *(begin + child))) break;
                    swap(*(begin + root), *(begin + child));
                    root = child;
                }
            }

            return;
        }

        // median of three, median ends up in *mid, then moves to *begin as the pivot
        I mid = begin + n / 2;
        I last = end - 1;

        if (pred(*mid, *begin)) swap(*mid, *begin);
        if (pred(*last, *mid))
        {
            swap(*last, *mid);
            if (pred(*mid, *begin)) swap(*mid, *begin);
        }

        swap(*begin, *mid);

        I i = begin + 1;
        I j = end;

        for (;;)
        {
            while (i < j && pred(*i, *begin)) ++i;
            while (i < j && pred(*begin, *(j - 1))) --j;

            if (i >= j) break;

            swap(*i, *(j - 1));
            ++i;
            --j;
        }

        I p = i - 1;
        swap(*begin, *p);

        // recurse into the smaller part, iterate on the larger one
        if (p - begin < end - (p + 1))
        {
            sort(begin, p, pred);
            begin = p + 1;
        }
        else
        {
            sort(p + 1, end, pred);
            end = p;
        }

        n = end - begin;
    }

    // insertion sort for short ranges
    if (n < 2) return;

    for (I i = begin + 1; i != end; ++i)
    {
        for (I j = i; j != begin && pred(*j, *(j - 1)); --j)
            swap(*j, *(j - 1));
    }
}
```
