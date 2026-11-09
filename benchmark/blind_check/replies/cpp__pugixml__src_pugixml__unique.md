```cpp
template <typename I> PUGI__FN I unique(I begin, I end)
{
    if (begin == end) return begin;

    // find first duplicate; nothing before it needs to be moved
    I first = begin;
    I next = first + 1;

    while (next != end && *first != *next)
    {
        first = next;
        ++next;
    }

    if (next == end) return end;

    // first is the last kept element, next is a duplicate of it
    I write = first + 1;

    for (++next; next != end; ++next)
    {
        if (*(write - 1) != *next)
        {
            *write = *next;
            ++write;
        }
    }

    return write;
}
```
