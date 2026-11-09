bool get_ubjson_object()
{
    std::pair<std::size_t, int> size_and_type;
    if (JSON_HEDLEY_UNLIKELY(not get_ubjson_size_type(size_and_type)))
    {
        return false;
    }

    string_t key;
    if (size_and_type.first != string_t::npos)
    {
        if (JSON_HEDLEY_UNLIKELY(not sax->start_object(size_and_type.first)))
        {
            return false;
        }

        if (size_and_type.second != 0)
        {
            for (std::size_t i = 0; i < size_and_type.first; ++i)
            {
                if (JSON_HEDLEY_UNLIKELY(not get_ubjson_string(key) or not sax->key(key)))
                {
                    return false;
                }
                if (JSON_HEDLEY_UNLIKELY(not get_ubjson_value(size_and_type.second)))
                {
                    return false;
                }
                key.clear();
            }
        }
        else
        {
            for (std::size_t i = 0; i < size_and_type.first; ++i)
            {
                if (JSON_HEDLEY_UNLIKELY(not get_ubjson_string(key) or not sax->key(key)))
                {
                    return false;
                }
                if (JSON_HEDLEY_UNLIKELY(not parse_ubjson_internal()))
                {
                    return false;
                }
                key.clear();
            }
        }
    }
    else
    {
        if (JSON_HEDLEY_UNLIKELY(not sax->start_object(std::size_t(-1))))
        {
            return false;
        }

        while (current != '}')
        {
            if (JSON_HEDLEY_UNLIKELY(not get_ubjson_string(key, false) or not sax->key(key)))
            {
                return false;
            }
            if (JSON_HEDLEY_UNLIKELY(not parse_ubjson_internal()))
            {
                return false;
            }
            get_ignore_noop();
            key.clear();
        }
    }

    return sax->end_object();
}
