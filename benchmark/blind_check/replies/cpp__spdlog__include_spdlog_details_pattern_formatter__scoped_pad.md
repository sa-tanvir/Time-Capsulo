```cpp
scoped_pad(size_t wrapped_size, padding_info &padinfo, fmt::memory_buffer &dest)
    : padinfo_(padinfo)
    , dest_(dest)
{
    total_pad_ = 0;
    if (padinfo_.width_ <= wrapped_size)
    {
        return;
    }

    const size_t total = padinfo_.width_ - wrapped_size;
    if (padinfo_.side_ == padding_info::left)
    {
        pad_it(total);
    }
    else if (padinfo_.side_ == padding_info::center)
    {
        const size_t half = total / 2;
        pad_it(half);
        total_pad_ = total - half;
    }
    else
    {
        total_pad_ = total;
    }
}
```
