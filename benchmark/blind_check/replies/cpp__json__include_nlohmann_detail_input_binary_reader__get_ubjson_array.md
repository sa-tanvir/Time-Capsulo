```cpp
bool get_ubjson_array()
{
    std::pair<std::size_t, int> size_and_type;
    if (JSON_HEDLEY_UNLIKELY(not get_ubjson_size_type(size_and_type)))
    {
        return false;
    }

    if (size_and_type.first != string_t::npos)
    {
        if (JSON_HEDLEY_UNLIKELY(not sax->start_array(size_and_type.first)))
        {
            return false;
        }

        if (size_and_type.second != 0)
        {
            if (size_and_type.second != 'N')
            {
                for (std::size_t i = 0; i < size_and_type.first; ++i)
                {
                    if (JSON_HEDLEY_UNLIKELY(not get_ubjson_value(size_and_type.second)))
                    {
                        return false;
                    }
                }
            }
        }
        else
        {
            for (std::size_t i = 0; i < size_and_type.first; ++i)
            {
                if (JSON_HEDLEY_UNLIKELY(not parse_ubjson_internal()))
                {
                    return false;
                }
            }
        }
    }
    else
    {
        if (JSON_HEDLEY_UNLIKELY(not sax->start_array(std::size_t(-1))))
        {
            return false;
        }

        while (current != ']')
        {
            if (JSON_HEDLEY_UNLIKELY(not parse_ubjson_internal(false)))
            {
                return false;
            }
            get_ignore_noop();
        }
    }

    return sax->end_array();
}
```
