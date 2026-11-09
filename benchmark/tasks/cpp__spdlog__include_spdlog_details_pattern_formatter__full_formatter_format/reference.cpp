    void format(const details::log_msg &msg, const std::tm &tm_time, fmt::memory_buffer &dest) override
    {
        using std::chrono::duration_cast;
        using std::chrono::milliseconds;
        using std::chrono::seconds;

#ifndef SPDLOG_NO_DATETIME

        // cache the date/time part for the next second.
        auto duration = msg.time.time_since_epoch();
        auto secs = duration_cast<seconds>(duration);

        if (cache_timestamp_ != secs || cached_datetime_.size() == 0)
        {
            cached_datetime_.clear();
            cached_datetime_.push_back('[');
            fmt_helper::append_int(tm_time.tm_year + 1900, cached_datetime_);
            cached_datetime_.push_back('-');

            fmt_helper::pad2(tm_time.tm_mon + 1, cached_datetime_);
            cached_datetime_.push_back('-');

            fmt_helper::pad2(tm_time.tm_mday, cached_datetime_);
            cached_datetime_.push_back(' ');

            fmt_helper::pad2(tm_time.tm_hour, cached_datetime_);
            cached_datetime_.push_back(':');

            fmt_helper::pad2(tm_time.tm_min, cached_datetime_);
            cached_datetime_.push_back(':');

            fmt_helper::pad2(tm_time.tm_sec, cached_datetime_);
            cached_datetime_.push_back('.');

            cache_timestamp_ = secs;
        }
        fmt_helper::append_buf(cached_datetime_, dest);

        auto millis = fmt_helper::time_fraction<milliseconds>(msg.time);
        fmt_helper::pad3(static_cast<uint32_t>(millis.count()), dest);
        dest.push_back(']');
        dest.push_back(' ');

#else // no datetime needed
        (void)tm_time;
#endif

#ifndef SPDLOG_NO_NAME
        if (!msg.logger_name->empty())
        {
            dest.push_back('[');
            // fmt_helper::append_str(*msg.logger_name, dest);
            fmt_helper::append_string_view(*msg.logger_name, dest);
            dest.push_back(']');
            dest.push_back(' ');
        }
#endif

        dest.push_back('[');
        // wrap the level name with color
        msg.color_range_start = dest.size();
        // fmt_helper::append_string_view(level::to_c_str(msg.level), dest);
        fmt_helper::append_string_view(level::to_string_view(msg.level), dest);
        msg.color_range_end = dest.size();
        dest.push_back(']');
        dest.push_back(' ');

        // add source location if present
        if (!msg.source.empty())
        {
            dest.push_back('[');
            fmt_helper::append_string_view(msg.source.filename, dest);
            dest.push_back(':');
            fmt_helper::append_int(msg.source.line, dest);
            dest.push_back(']');
            dest.push_back(' ');
        }
        // fmt_helper::append_string_view(msg.msg(), dest);
        fmt_helper::append_string_view(msg.payload, dest);
    }
