```cpp
token_type scan()
{
    // initially, skip the BOM
    if (position.chars_read_total == 0 and not skip_bom())
    {
        error_message = "invalid BOM; must be 0xEF 0xBB 0xBF if given";
        return token_type::parse_error;
    }

    // read next character and ignore whitespace
    do
    {
        get();
    }
    while (current == ' ' or current == '\t' or current == '\n' or current == '\r');

    switch (current)
    {
        // structural characters
        case '[':
            return token_type::begin_array;
        case ']':
            return token_type::end_array;
        case '{':
            return token_type::begin_object;
        case '}':
            return token_type::end_object;
        case ':':
            return token_type::name_separator;
        case ',':
            return token_type::value_separator;

        // literals
        case 't':
            return scan_literal("true", 4, token_type::literal_true);
        case 'f':
            return scan_literal("false", 5, token_type::literal_false);
        case 'n':
            return scan_literal("null", 4, token_type::literal_null);

        // string
        case '\"':
            return scan_string();

        // number
        case '-':
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            return scan_number();

        // end of input (the null byte is empty with respect to the input)
        case '\0':
        case std::char_traits<char>::eof():
            return token_type::end_of_input;

        // error
        default:
            error_message = "invalid literal";
            return token_type::parse_error;
    }
}
```
