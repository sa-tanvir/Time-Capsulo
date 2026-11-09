```cpp
inline void pad_uint(T n, unsigned int width, fmt::basic_memory_buffer<char, Buffer_Size> &dest)
{
    static_assert(std::is_unsigned<T>::value, "pad_uint must get unsigned T");
    auto digits = static_cast<unsigned int>(count_digits(n));
    for (; digits < width; ++digits)
    {
        dest.push_back('0');
    }
    append_int(n, dest);
}
```
