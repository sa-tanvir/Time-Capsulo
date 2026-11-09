inline void pad2(int n, fmt::basic_memory_buffer<char, Buffer_Size> &dest)
{
    if (n > 99)
    {
        append_int(n, dest);
    }
    else if (n > 9) // 10-99
    {
        dest.push_back(static_cast<char>('0' + n / 10));
        dest.push_back(static_cast<char>('0' + n % 10));
    }
    else if (n >= 0) // 0-9
    {
        dest.push_back('0');
        dest.push_back(static_cast<char>('0' + n));
    }
    else // negatives (unlikely, but just in case, let fmt deal with it)
    {
        fmt::format_to(dest, "{:02}", n);
    }
}
