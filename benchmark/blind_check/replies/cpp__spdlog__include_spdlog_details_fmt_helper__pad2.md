```cpp
inline void pad2(int n, fmt::basic_memory_buffer<char, Buffer_Size> &dest)
{
    if (n >= 0 && n < 100)
    {
        dest.push_back(static_cast<char>('0' + n / 10));
        dest.push_back(static_cast<char>('0' + n % 10));
    }
    else
    {
        append_int(n, dest);
    }
}
```
