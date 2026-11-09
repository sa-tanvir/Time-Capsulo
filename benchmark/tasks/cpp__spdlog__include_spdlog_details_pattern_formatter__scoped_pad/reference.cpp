scoped_pad(size_t wrapped_size, padding_info &padinfo, fmt::memory_buffer &dest)
    : padinfo_(padinfo)
    , dest_(dest)
{

    if (padinfo_.width_ <= wrapped_size)
    {
        total_pad_ = 0;
        return;
    }

    total_pad_ = padinfo.width_ - wrapped_size;
    if (padinfo_.side_ == padding_info::left)
    {
        pad_it(total_pad_);
        total_pad_ = 0;
    }
    else if (padinfo_.side_ == padding_info::center)
    {
        auto half_pad = total_pad_ / 2;
        auto reminder = total_pad_ & 1;
        pad_it(half_pad);
        total_pad_ = half_pad + reminder; // for the right side
    }
}
