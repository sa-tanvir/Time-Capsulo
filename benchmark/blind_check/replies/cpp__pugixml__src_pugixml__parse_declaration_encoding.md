```cpp
PUGI__FN bool parse_declaration_encoding(const uint8_t* data, size_t size, const uint8_t*& out_encoding, size_t& out_length)
{
    #define PUGI__SCANCHAR(ch) { if (offset >= size || data[offset] != ch) return false; offset++; }
    #define PUGI__SCANCHARTYPE(ct) { while (offset < size && PUGI__IS_CHARTYPE(data[offset], ct)) offset++; }

    if (size < 6 || data[0] != '<' || data[1] != '?' || data[2] != 'x' || data[3] != 'm' || data[4] != 'l' ||
        !PUGI__IS_CHARTYPE(data[5], ct_space))
        return false;

    size_t offset = 6;

    while (offset + 1 < size)
    {
        uint8_t c = data[offset];

        if (c == '?')
            return false;

        if (c == 'e' && data[offset + 1] == 'n')
        {
            PUGI__SCANCHAR('e'); PUGI__SCANCHAR('n'); PUGI__SCANCHAR('c'); PUGI__SCANCHAR('o');
            PUGI__SCANCHAR('d'); PUGI__SCANCHAR('i'); PUGI__SCANCHAR('n'); PUGI__SCANCHAR('g');

            PUGI__SCANCHARTYPE(ct_space);
            PUGI__SCANCHAR('=');
            PUGI__SCANCHARTYPE(ct_space);

            uint8_t delimiter = (offset < size && data[offset] == '"') ? '"' : '\'';

            PUGI__SCANCHAR(delimiter);

            size_t start = offset;

            PUGI__SCANCHARTYPE(ct_symbol);

            size_t end = offset;

            PUGI__SCANCHAR(delimiter);

            out_encoding = data + start;
            out_length = end - start;

            return true;
        }

        offset++;
    }

    return false;

    #undef PUGI__SCANCHAR
    #undef PUGI__SCANCHARTYPE
}
```
