```cpp
BasicJsonType& get_unchecked(BasicJsonType* ptr) const
{
    for (const auto& reference_token : reference_tokens)
    {
        // convert null values to arrays or objects before continuing
        if (ptr->type() == detail::value_t::null)
        {
            // check if reference token is a number
            const bool nums =
                std::all_of(reference_token.begin(), reference_token.end(),
                            [](const char x)
            {
                return (x >= '0' and x <= '9');
            });

            // change value to array for numbers or "-" or to object otherwise
            *ptr = (nums or reference_token == "-")
                   ? detail::value_t::array
                   : detail::value_t::object;
        }

        switch (ptr->type())
        {
            case detail::value_t::object:
            {
                // use unchecked object access
                ptr = &ptr->operator[](reference_token);
                break;
            }

            case detail::value_t::array:
            {
                if (reference_token.size() > 1 and reference_token[0] == '0')
                {
                    JSON_THROW(detail::parse_error::create(106, 0,
                                                           "array index '" + reference_token +
                                                           "' must not begin with '0'"));
                }

                if (reference_token == "-")
                {
                    // explicitly treat "-" as index beyond the end
                    ptr = &ptr->operator[](ptr->size());
                }
                else
                {
                    // convert array index to number; unchecked access
                    int idx = 0;
                    JSON_TRY
                    {
                        idx = array_index(reference_token);
                    }
                    JSON_CATCH(std::invalid_argument&)
                    {
                        JSON_THROW(detail::parse_error::create(109, 0, "array index '" + reference_token + "' is not a number"));
                    }
                    ptr = &ptr->operator[](static_cast<std::size_t>(idx));
                }
                break;
            }

            default:
            {
                JSON_THROW(detail::out_of_range::create(404, "unresolved reference token '" + reference_token + "'"));
            }
        }
    }

    return *ptr;
}
```
