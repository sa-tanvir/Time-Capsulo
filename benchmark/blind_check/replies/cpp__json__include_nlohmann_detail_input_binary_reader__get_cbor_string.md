```cpp
bool get_cbor_string(string_t& result)
{
    if (JSON_HEDLEY_UNLIKELY(not unexpect_eof(input_format_t::cbor, "string")))
    {
        return false;
    }

    switch (current)
    {
        // UTF-8 string (0x00..0x17 bytes follow)
        case 0x60:
        case 0x61:
        case 0x62:
        case 0x63:
        case 0x64:
        case 0x65:
        case 0x66:
        case 0x67:
        case 0x68:
        case 0x69:
        case 0x6A:
        case 0x6B:
        case 0x6C:
        case 0x6D:
        case 0x6E:
        case 0x6F:
        case 0x70:
        case 0x71:
        case 0x72:
        case 0x73:
        case 0x74:
        case 0x75:
        case 0x76:
        case 0x77:
        {
            return get_string(input_format_t::cbor, static_cast<unsigned int>(current) & 0x1Fu, result);
        }

        case 0x78: // UTF-8 string (one-byte uint8_t for n follows)
        {
            std::uint8_t len;
            return get_number(input_format_t::cbor, len) and get_string(input_format_t::cbor, len, result);
        }

        case 0x79: // UTF-8 string (two-byte uint16_t for n follow)
        {
            std::uint16_t len;
            return get_number(input_format_t::cbor, len) and get_string(input_format_t::cbor, len, result);
        }

        case 0x7A: // UTF-8 string (four-byte uint32_t for n follow)
        {
            std::uint32_t len;
            return get_number(input_format_t::cbor, len) and get_string(input_format_t::cbor, len, result);
        }

        case 0x7B: // UTF-8 string (eight-byte uint64_t for n follow)
        {
            std::uint64_t len;
            return get_number(input_format_t::cbor, len) and get_string(input_format_t::cbor, len, result);
        }

        case 0x7F: // UTF-8 string (indefinite length)
        {
            while (get() != 0xFF)
            {
                string_t chunk;
                if (not get_cbor_string(chunk))
                {
                    return false;
                }
                result.append(chunk);
            }
            return true;
        }

        default:
        {
            auto last_token = get_token_string();
            return sax->parse_error(chars_read, last_token, parse_error::create(113, chars_read, exception_message(input_format_t::cbor, "expected length specification (0x60-0x7B) or indefinite string type (0x7F); last byte: 0x" + last_token, "string")));
        }
    }
}
```
