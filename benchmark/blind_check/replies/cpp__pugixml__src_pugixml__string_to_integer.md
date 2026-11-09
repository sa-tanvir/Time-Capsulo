```cpp
template <typename U> PUGI__FN PUGI__UNSIGNED_OVERFLOW U string_to_integer(const char_t* value, U minv, U maxv)
{
    const char_t* s = value;

    while (PUGI__IS_CHARTYPE(*s, ct_space))
        s++;

    bool negative = (*s == '-');

    if (*s == '-' || *s == '+')
        s++;

    const U maxu = static_cast<U>(~static_cast<U>(0));

    U result = 0;
    bool overflow = false;

    if (s[0] == '0' && (s[1] == 'x' || s[1] == 'X'))
    {
        s += 2;

        const U limit = static_cast<U>(maxu / 16);

        for (;; ++s)
        {
            unsigned int ch = static_cast<unsigned char>(*s);
            unsigned int d;

            if (ch - '0' <= 9) d = ch - '0';
            else if ((ch | 0x20) - 'a' <= 5) d = (ch | 0x20) - 'a' + 10;
            else break;

            if (result > limit)
            {
                overflow = true;
                break;
            }

            result = static_cast<U>(result * 16 + d);
        }
    }
    else
    {
        const U limit = static_cast<U>(maxu / 10);
        const unsigned int rem = static_cast<unsigned int>(maxu % 10);

        for (;; ++s)
        {
            unsigned int d = static_cast<unsigned char>(*s) - '0';

            if (d > 9) break;

            if (result > limit || (result == limit && d > rem))
            {
                overflow = true;
                break;
            }

            result = static_cast<U>(result * 10 + d);
        }
    }

    if (negative)
    {
        U absmin = static_cast<U>(0 - minv);

        if (overflow || result > absmin)
            return minv;

        return static_cast<U>(0 - result);
    }

    if (overflow || result > maxv)
        return maxv;

    return result;
}
```
