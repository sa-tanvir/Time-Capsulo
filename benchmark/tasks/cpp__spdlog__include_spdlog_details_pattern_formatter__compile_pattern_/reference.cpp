void compile_pattern_(const std::string &pattern)
{
    auto end = pattern.end();
    std::unique_ptr<details::aggregate_formatter> user_chars;
    formatters_.clear();
    for (auto it = pattern.begin(); it != end; ++it)
    {
        if (*it == '%')
        {
            if (user_chars) // append user chars found so far
            {
                formatters_.push_back(std::move(user_chars));
            }

            auto padding = handle_padspec_(++it, end);

            if (it != end)
            {
                handle_flag_(*it, padding);
            }
            else
            {
                break;
            }
        }
        else // chars not following the % sign should be displayed as is
        {
            if (!user_chars)
            {
                user_chars = details::make_unique<details::aggregate_formatter>();
            }
            user_chars->add_ch(*it);
        }
    }
    if (user_chars) // append raw chars found so far
    {
        formatters_.push_back(std::move(user_chars));
    }
}
