```cpp
void format(const details::log_msg &msg, const std::tm &, fmt::memory_buffer &dest) override
{
    scoped_pad p(msg.logger_name->size(), padinfo_, dest);
    fmt_helper::append_string_view(string_view_t(msg.logger_name->data(), msg.logger_name->size()), dest);
}
```
