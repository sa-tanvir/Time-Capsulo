```cpp
PUGI__FN xpath_string convert_number_to_string(double value, xpath_allocator* alloc)
{
    if (const char_t* special = convert_number_to_string_special(value))
        return xpath_string::from_const(special);

    char buffer[32];
    char* mantissa;
    int exponent;
    convert_number_to_mantissa_exponent(value, buffer, &mantissa, &exponent);

    size_t digits = strlen(mantissa);
    size_t sign = value < 0 ? 1 : 0;

    size_t int_len = exponent > 0 ? static_cast<size_t>(exponent) : 1;
    size_t frac_len = 0;
    if (static_cast<int>(digits) > exponent)
    {
        size_t rest = exponent > 0 ? digits - static_cast<size_t>(exponent) : digits;
        size_t zeros = exponent < 0 ? static_cast<size_t>(-exponent) : 0;
        frac_len = 1 + zeros + rest;
    }

    size_t total = sign + int_len + frac_len;

    char_t* result = static_cast<char_t*>(alloc->allocate((total + 1) * sizeof(char_t)));
    if (!result) return xpath_string();

    char_t* s = result;
    if (sign) *s++ = '-';

    const char* m = mantissa;
    const char* mend = mantissa + digits;

    if (exponent > 0)
    {
        size_t n = static_cast<size_t>(exponent);
        size_t have = digits < n ? digits : n;
        for (size_t i = 0; i < have; ++i) *s++ = *m++;
        for (size_t i = have; i < n; ++i) *s++ = '0';
    }
    else
    {
        *s++ = '0';
    }

    if (m < mend)
    {
        *s++ = '.';
        for (int i = exponent; i < 0; ++i) *s++ = '0';
        while (m < mend) *s++ = *m++;
    }

    *s = 0;

    return xpath_string::from_heap_preallocated(result, s);
}
```
