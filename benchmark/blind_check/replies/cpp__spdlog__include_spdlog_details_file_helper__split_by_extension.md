```cpp
static std::tuple<filename_t, filename_t> split_by_extension(const spdlog::filename_t &fname)
{
    auto ext_index = fname.rfind('.');

    // no dot, leading dot (hidden file) or trailing dot: no extension
    if (ext_index == filename_t::npos || ext_index == 0 || ext_index == fname.size() - 1)
    {
        return std::make_tuple(fname, filename_t());
    }

    // dot belongs to a folder name or directly follows a separator
    auto folder_index = fname.rfind(spdlog::details::os::folder_sep);
    if (folder_index != filename_t::npos && folder_index >= ext_index - 1)
    {
        return std::make_tuple(fname, filename_t());
    }

    return std::make_tuple(fname.substr(0, ext_index), fname.substr(ext_index));
}
```
