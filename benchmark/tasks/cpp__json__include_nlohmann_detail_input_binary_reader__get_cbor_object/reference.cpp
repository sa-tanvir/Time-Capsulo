bool get_cbor_object(const std::size_t len)
{
    if (JSON_HEDLEY_UNLIKELY(not sax->start_object(len)))
    {
        return false;
    }

    string_t key;
    if (len != std::size_t(-1))
    {
        for (std::size_t i = 0; i < len; ++i)
        {
            get();
            if (JSON_HEDLEY_UNLIKELY(not get_cbor_string(key) or not sax->key(key)))
            {
                return false;
            }

            if (JSON_HEDLEY_UNLIKELY(not parse_cbor_internal()))
            {
                return false;
            }
            key.clear();
        }
    }
    else
    {
        while (get() != 0xFF)
        {
            if (JSON_HEDLEY_UNLIKELY(not get_cbor_string(key) or not sax->key(key)))
            {
                return false;
            }

            if (JSON_HEDLEY_UNLIKELY(not parse_cbor_internal()))
            {
                return false;
            }
            key.clear();
        }
    }

    return sax->end_object();
}
