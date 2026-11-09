```cpp
void format(const details::log_msg &msg, const std::tm &, fmt::memory_buffer &dest) override
{
    const string_view_t &level_name = level::to_string_view(msg.level);
    scoped_pad p(level_name, padinfo_, dest);
    fmt_helper::append_string_view(level_name, dest);
}
```
