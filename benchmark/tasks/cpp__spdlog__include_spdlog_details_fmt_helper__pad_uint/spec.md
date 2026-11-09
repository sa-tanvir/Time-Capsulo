# Functional specification: `fmt_helper::pad_uint(n, width, dest)`

## 1. Component overview

A formatting helper of spdlog used to write the fractional-second fields of a timestamp (milliseconds, microseconds, nanoseconds) and the message counter. It appends an unsigned integer to a character buffer in decimal, left-padded with `0` characters to a minimum number of digits.

## 2. Functional requirements

Appends to the end of `dest` (existing content is kept) the decimal representation of `n`, preceded by as many `0` characters as are needed for the whole appended text to have at least `width` characters:

1. Let `d` be the number of decimal digits of `n` (`d == 1` for `n == 0`).
2. If `width > d`, append `width - d` zero characters first.
3. Then append the digits of `n` (no sign, no separators, no leading zeros of its own).

The number is never truncated: if `n` has more digits than `width`, only its digits are appended. `width == 0` therefore means "no padding".

## 3. Input specification

- `n`: a value of the unsigned integer type `T` (`unsigned short`, `unsigned int`, `unsigned long`, `unsigned long long`; the full range of the type, e.g. up to 18446744073709551615 for 64 bits).
- `width`: `unsigned int`, from 0 to 20 inclusive (larger widths are outside the contract).
- `dest`: a `fmt::basic_memory_buffer<char, Buffer_Size>`, possibly already containing text.

## 4. Output specification

No return value; only `dest` grows by the text described above. No exceptions for valid input.

## 5. Edge cases and constraints

| `n` | `width` | appended |
|---|---|---|
| 0 | 3 | `000` |
| 3 | 3 | `003` |
| 123 | 3 | `123` |
| 1234 | 3 | `1234` |
| 12345 | 6 | `012345` |
| 123456789 | 9 | `123456789` |
| 1234567891 | 9 | `1234567891` |
| 7 | 0 | `7` |
| 7 | 1 | `7` |
| 0 | 1 | `0` |
| 42 | 12 | `000000000042` |
| 18446744073709551615 | 20 | `18446744073709551615` |
| 18446744073709551615 | 3 | `18446744073709551615` |

The helper is called for every logged line, so it must be fast and avoid temporary allocations.
