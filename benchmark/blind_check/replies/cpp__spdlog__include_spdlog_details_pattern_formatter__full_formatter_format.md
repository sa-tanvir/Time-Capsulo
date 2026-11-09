```cpp
void format(const details::log_msg &msg, const std::tm &tm_time, fmt::memory_buffer &dest) override
{
    using namespace fmt_helper;

    dest.push_back('[');
    append_int(tm_time.tm_year + 1900, dest);
    dest.push_back('-');
    pad2(tm_time.tm_mon + 1, dest);
    dest.push_back('-');
    pad2(tm_time.tm_mday, dest);
    dest.push_back(' ');
    pad2(tm_time.tm_hour, dest);
    dest.push_back(':');
    pad2(tm_time.tm_min, dest);
    dest.push_back(':');
    pad2(tm_time.tm_sec, dest);
    dest.push_back('.');
    auto millis = fmt_helper::time_fraction<std::chrono::milliseconds>(msg.time);
    pad3(static_cast<uint32_t>(millis.count()), dest);
    dest.push_back(']');
    dest.push_back(' ');

    if (!msg.logger_name->empty())
    {
        dest.push_back('[');
        append_string_view(string_view_t(msg.logger_name->data(), msg.logger_name->size()), dest);
        dest.push_back(']');
        dest.push_back(' ');
    }

    dest.push_back('[');
    msg.color_range_start = dest.size();
    append_string_view(level::to_string_view(msg.level), dest);
    msg.color_range_end = dest.size();
    dest.push_back(']');
    dest.push_back(' ');

    if (!msg.source.empty())
    {
        dest.push_back('[');
        const char *filename = msg.source.filename;
        append_string_view(string_view_t(filename), dest);
        dest.push_back(':');
        append_int(msg.source.line, dest);
        dest.push_back(']');
        dest.push_back(' ');
    }

    append_string_view(msg.payload, dest);
}
```
