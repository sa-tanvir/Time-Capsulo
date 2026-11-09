inline void pad_uint(T n, unsigned int width, fmt::basic_memory_buffer<char, Buffer_Size> &dest)
{
    static_assert(std::is_unsigned<T>::value, "pad_uint must get unsigned T");
    auto digits = count_digits(n);
    if (width > digits)
    {
        const char *zeroes = "0000000000000000000";
        dest.append(zeroes, zeroes + width - digits);
    }
    append_int(n, dest);
}
