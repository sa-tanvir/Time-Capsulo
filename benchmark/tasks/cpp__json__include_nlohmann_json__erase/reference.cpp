IteratorType erase(IteratorType first, IteratorType last)
{
    // make sure iterator fits the current value
    if (JSON_HEDLEY_UNLIKELY(this != first.m_object or this != last.m_object))
    {
        JSON_THROW(invalid_iterator::create(203, "iterators do not fit current value"));
    }

    IteratorType result = end();

    switch (m_type)
    {
        case value_t::boolean:
        case value_t::number_float:
        case value_t::number_integer:
        case value_t::number_unsigned:
        case value_t::string:
        {
            if (JSON_HEDLEY_LIKELY(not first.m_it.primitive_iterator.is_begin()
                                   or not last.m_it.primitive_iterator.is_end()))
            {
                JSON_THROW(invalid_iterator::create(204, "iterators out of range"));
            }

            if (is_string())
            {
                AllocatorType<string_t> alloc;
                std::allocator_traits<decltype(alloc)>::destroy(alloc, m_value.string);
                std::allocator_traits<decltype(alloc)>::deallocate(alloc, m_value.string, 1);
                m_value.string = nullptr;
            }

            m_type = value_t::null;
            assert_invariant();
            break;
        }

        case value_t::object:
        {
            result.m_it.object_iterator = m_value.object->erase(first.m_it.object_iterator,
                                          last.m_it.object_iterator);
            break;
        }

        case value_t::array:
        {
            result.m_it.array_iterator = m_value.array->erase(first.m_it.array_iterator,
                                         last.m_it.array_iterator);
            break;
        }

        default:
            JSON_THROW(type_error::create(307, "cannot use erase() with " + std::string(type_name())));
    }

    return result;
}
