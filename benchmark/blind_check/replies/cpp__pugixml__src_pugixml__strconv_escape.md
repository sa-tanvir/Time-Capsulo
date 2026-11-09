```cpp
PUGI__FN char_t* strconv_escape(char_t* s, gap& g)
{
    char_t* stre = s + 1;

    switch (*stre)
    {
    case '#':
    {
        unsigned int ucsc = 0;
        char_t* p = stre + 1;

        if (*p == 'x')
        {
            ++p;
            char_t* digits = p;

            for (;; ++p)
            {
                char_t ch = *p;

                if (static_cast<unsigned>(ch - '0') <= 9)
                    ucsc = 16 * ucsc + static_cast<unsigned>(ch - '0');
                else if (static_cast<unsigned>((ch | 0x20) - 'a') <= 5 && ch >= 'A')
                    ucsc = 16 * ucsc + static_cast<unsigned>((ch | 0x20) - 'a') + 10;
                else
                    break;
            }

            if (p == digits || *p != ';') return p;
        }
        else
        {
            char_t* digits = p;

            for (; static_cast<unsigned>(*p - '0') <= 9; ++p)
                ucsc = 10 * ucsc + static_cast<unsigned>(*p - '0');

            if (p == digits || *p != ';') return p;
        }

        char_t* end = p + 1;
        char_t* out = reinterpret_cast<char_t*>(utf8_writer::any(reinterpret_cast<uint8_t*>(s), ucsc));

        g.push(out, static_cast<size_t>(end - out));
        return end;
    }

    case 'a':
    {
        char_t* p = stre + 1;

        if (*p == 'm')
        {
            if (p[1] != 'p') return p + 1;
            if (p[2] != ';') return p + 2;

            *s = '&';
            char_t* out = s + 1;
            g.push(out, 4);
            return s + 5;
        }
        else if (*p == 'p')
        {
            if (p[1] != 'o') return p + 1;
            if (p[2] != 's') return p + 2;
            if (p[3] != ';') return p + 3;

            *s = '\'';
            char_t* out = s + 1;
            g.push(out, 5);
            return s + 6;
        }

        return p;
    }

    case 'g':
    {
        char_t* p = stre + 1;

        if (*p != 't') return p;
        if (p[1] != ';') return p + 1;

        *s = '>';
        char_t* out = s + 1;
        g.push(out, 3);
        return s + 4;
    }

    case 'l':
    {
        char_t* p = stre + 1;

        if (*p != 't') return p;
        if (p[1] != ';') return p + 1;

        *s = '<';
        char_t* out = s + 1;
        g.push(out, 3);
        return s + 4;
    }

    case 'q':
    {
        char_t* p = stre + 1;

        if (*p != 'u') return p;
        if (p[1] != 'o') return p + 1;
        if (p[2] != 't') return p + 2;
        if (p[3] != ';') return p + 3;

        *s = '"';
        char_t* out = s + 1;
        g.push(out, 5);
        return s + 6;
    }

    default:
        return stre;
    }
}
```
