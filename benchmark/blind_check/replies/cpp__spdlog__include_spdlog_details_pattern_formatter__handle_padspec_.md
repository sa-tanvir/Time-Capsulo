```cpp
details::padding_info handle_padspec_(std::string::const_iterator &it, std::string::const_iterator end)
{
    using details::padding_info;
    using details::scoped_pad;

    if (it == end)
    {
        return padding_info();
    }

    padding_info::pad_side side = padding_info::left;
    if (*it == '-')
    {
        side = padding_info::right;
        ++it;
    }
    else if (*it == '=')
    {
        side = padding_info::center;
        ++it;
    }

    if (it == end || !std::isdigit(static_cast<unsigned char>(*it)))
    {
        return padding_info(0, side);
    }

    size_t width = 0;
    for (; it != end && std::isdigit(static_cast<unsigned char>(*it)); ++it)
    {
        if (width < 1000) // saturate, anything above 128 is clamped anyway
        {
            width = width * 10 + static_cast<size_t>(*it - '0');
        }
    }
    return padding_info(std::min<size_t>(width, 128), side);
}
```
