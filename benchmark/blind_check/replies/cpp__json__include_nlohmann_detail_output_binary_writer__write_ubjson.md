```cpp
void write_ubjson(const BasicJsonType& j, const bool use_count,
                  const bool use_type, const bool add_prefix = true)
{
    switch (j.type())
    {
        case value_t::null:
        {
            if (add_prefix)
            {
                oa->write_character(to_char_type('Z'));
            }
            break;
        }

        case value_t::boolean:
        {
            if (add_prefix)
            {
                oa->write_character(j.m_value.boolean
                                    ? to_char_type('T')
                                    : to_char_type('F'));
            }
            break;
        }

        case value_t::number_integer:
        {
            write_number_with_ubjson_prefix(j.m_value.number_integer, add_prefix);
            break;
        }

        case value_t::number_unsigned:
        {
            write_number_with_ubjson_prefix(j.m_value.number_unsigned, add_prefix);
            break;
        }

        case value_t::number_float:
        {
            write_number_with_ubjson_prefix(j.m_value.number_float, add_prefix);
            break;
        }

        case value_t::string:
        {
            if (add_prefix)
            {
                oa->write_character(to_char_type('S'));
            }
            write_number_with_ubjson_prefix(j.m_value.string->size(), true);
            oa->write_characters(
                reinterpret_cast<const CharType*>(j.m_value.string->c_str()),
                j.m_value.string->size());
            break;
        }

        case value_t::array:
        {
            if (add_prefix)
            {
                oa->write_character(to_char_type('['));
            }

            bool prefix_required = true;
            if (use_type and not j.m_value.array->empty())
            {
                const CharType first_prefix = ubjson_prefix(j.front());
                const bool same_prefix = std::all_of(j.begin() + 1, j.end(),
                                                     [this, first_prefix](const BasicJsonType & v)
                {
                    return ubjson_prefix(v) == first_prefix;
                });

                if (same_prefix)
                {
                    prefix_required = false;
                    oa->write_character(to_char_type('$'));
                    oa->write_character(first_prefix);
                }
            }

            if (use_count)
            {
                oa->write_character(to_char_type('#'));
                write_number_with_ubjson_prefix(j.m_value.array->size(), true);
            }

            for (const auto& el : *j.m_value.array)
            {
                write_ubjson(el, use_count, use_type, prefix_required);
            }

            if (not use_count)
            {
                oa->write_character(to_char_type(']'));
            }

            break;
        }

        case value_t::object:
        {
            if (add_prefix)
            {
                oa->write_character(to_char_type('{'));
            }

            bool prefix_required = true;
            if (use_type and not j.m_value.object->empty())
            {
                const CharType first_prefix = ubjson_prefix(j.front());
                const bool same_prefix = std::all_of(j.begin(), j.end(),
                                                     [this, first_prefix](const BasicJsonType & v)
                {
                    return ubjson_prefix(v) == first_prefix;
                });

                if (same_prefix)
                {
                    prefix_required = false;
                    oa->write_character(to_char_type('$'));
                    oa->write_character(first_prefix);
                }
            }

            if (use_count)
            {
                oa->write_character(to_char_type('#'));
                write_number_with_ubjson_prefix(j.m_value.object->size(), true);
            }

            for (const auto& el : *j.m_value.object)
            {
                write_number_with_ubjson_prefix(el.first.size(), true);
                oa->write_characters(
                    reinterpret_cast<const CharType*>(el.first.c_str()),
                    el.first.size());
                write_ubjson(el.second, use_count, use_type, prefix_required);
            }

            if (not use_count)
            {
                oa->write_character(to_char_type('}'));
            }

            break;
        }

        default:
            break;
    }
}
```
