```cpp
template <typename Traits> static inline typename Traits::value_type process(const uint8_t* data, size_t size, typename Traits::value_type result, Traits)
{
    const uint8_t* end = data + size;

    while (data < end)
    {
        uint8_t lead = *data;

        if (lead < 0x80)
        {
            result = Traits::low(result, lead);
            data += 1;
        }
        else if (lead < 0xC0)
        {
            // stray continuation byte
            data += 1;
        }
        else if (lead < 0xE0)
        {
            if (end - data >= 2 && (data[1] & 0xC0) == 0x80)
            {
                result = Traits::low(result, ((lead & 0x1Fu) << 6) | (data[1] & 0x3Fu));
                data += 2;
            }
            else data += 1;
        }
        else if (lead < 0xF0)
        {
            if (end - data >= 3 && (data[1] & 0xC0) == 0x80 && (data[2] & 0xC0) == 0x80)
            {
                result = Traits::low(result, ((lead & 0x0Fu) << 12) | ((data[1] & 0x3Fu) << 6) | (data[2] & 0x3Fu));
                data += 3;
            }
            else data += 1;
        }
        else if (lead < 0xF8)
        {
            if (end - data >= 4 && (data[1] & 0xC0) == 0x80 && (data[2] & 0xC0) == 0x80 && (data[3] & 0xC0) == 0x80)
            {
                result = Traits::high(result, ((lead & 0x07u) << 18) | ((data[1] & 0x3Fu) << 12) | ((data[2] & 0x3Fu) << 6) | (data[3] & 0x3Fu));
                data += 4;
            }
            else data += 1;
        }
        else
        {
            data += 1;
        }
    }

    return result;
}
```
