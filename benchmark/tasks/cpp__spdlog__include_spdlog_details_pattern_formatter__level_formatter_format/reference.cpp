void format(const details::log_msg &msg, const std::tm &, fmt::memory_buffer &dest) override
{
    string_view_t &level_name = level::to_string_view(msg.level);
    if (padinfo_.enabled())
    {
        scoped_pad p(level_name, padinfo_, dest);
        fmt_helper::append_string_view(level_name, dest);
    }
    else
    {
        fmt_helper::append_string_view(level_name, dest);
    }
}
