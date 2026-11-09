```cpp
IteratorType erase(IteratorType pos)
{
    // make sure iterator fits the current value
    if (JSON_HEDLEY_UNLIKELY(this != pos.m_object))
    {
        JSON_THROW(detail::invalid_iterator::create(202, "iterator does not fit current value"));
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
            if (JSON_HEDLEY_UNLIKELY(not pos.m_it.primitive_iterator.is_begin()))
            {
                JSON_THROW(detail::invalid_iterator::create(205, "iterator out of range"));
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
            result.m_it.object_iterator = m_value.object->erase(pos.m_it.object_iterator);
            break;
        }

        case value_t::array:
        {
            result.m_it.array_iterator = m_value.array->erase(pos.m_it.array_iterator);
            break;
        }

        default:
            JSON_THROW(detail::type_error::create(307, "cannot use erase() with " + std::string(type_name())));
    }

    return result;
}
```
