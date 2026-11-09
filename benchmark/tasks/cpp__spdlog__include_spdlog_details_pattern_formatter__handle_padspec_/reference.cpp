details::padding_info handle_padspec_(std::string::const_iterator &it, std::string::const_iterator end)
{
    using details::padding_info;
    using details::scoped_pad;
    const size_t max_width = 128;
    if (it == end)
    {
        return padding_info{};
    }

    padding_info::pad_side side;
    switch (*it)
    {
    case '-':
        side = padding_info::right;
        ++it;
        break;
    case '=':
        side = padding_info::center;
        ++it;
        break;
    default:
        side = details::padding_info::left;
        break;
    }

    if (it == end || !std::isdigit(static_cast<unsigned char>(*it)))
    {
        return padding_info{0, side};
    }

    auto width = static_cast<size_t>(*it - '0');
    for (++it; it != end && std::isdigit(static_cast<unsigned char>(*it)); ++it)
    {
        auto digit = static_cast<size_t>(*it - '0');
        width = width * 10 + digit;
    }
    return details::padding_info{std::min<size_t>(width, max_width), side};
}
