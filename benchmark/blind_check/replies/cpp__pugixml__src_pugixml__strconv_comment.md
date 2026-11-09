```cpp
PUGI__FN char_t* strconv_comment(char_t* s, char_t endch)
{
    char_t* r = s; // read position
    char_t* w = s; // write position, never ahead of r

    for (;;)
    {
        // fast scan over ordinary characters
        if (r == w)
        {
            while (!PUGI__IS_CHARTYPE(*r, ct_parse_comment)) ++r;
            w = r;
        }
        else
        {
            while (!PUGI__IS_CHARTYPE(*r, ct_parse_comment)) *w++ = *r++;
        }

        char_t c = *r;

        if (c == '\r')
        {
            *w++ = '\n';
            ++r;
            if (*r == '\n') ++r;
        }
        else if (c == '-')
        {
            if (r[1] == '-' && PUGI__ENDSWITH(r[2], '>'))
            {
                *w = 0;
                return r[2] == 0 ? r + 2 : r + 3;
            }

            *w++ = *r++;
        }
        else if (c == 0)
        {
            return 0;
        }
        else
        {
            // '>' or other stop character that is ordinary text
            *w++ = *r++;
        }
    }
}
```
