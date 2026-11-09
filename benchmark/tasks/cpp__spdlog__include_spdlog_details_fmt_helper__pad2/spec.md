# Functional specification: `fmt_helper::pad2(n, dest)`

## 1. Component overview

A formatting helper of spdlog used to write the two-digit fields of a timestamp (month, day, hour, minute, second). It appends the decimal representation of a small integer to a character buffer, zero-padded to at least two digits.

## 2. Functional requirements

The function appends characters to the end of `dest` (it never removes or changes what is already in `dest`):

1. `n` in 0..9: a `0` followed by the digit (`"00"`, `"03"`, `"09"`).
2. `n` in 10..99: the two decimal digits (`"10"`, `"23"`, `"99"`).
3. `n` greater than 99: the plain decimal representation, with no padding and no truncation (`"100"`, `"123"`, `"1234"`, `"2147483647"`).
4. `n` negative: the plain decimal representation with a leading minus sign and no extra zeros (`-5` gives `"-5"`, `-100` gives `"-100"`, `-2147483648` gives `"-2147483648"`).

## 3. Input specification

- `n`: any `int`.
- `dest`: a `fmt::basic_memory_buffer<char, Buffer_Size>` (any `Buffer_Size`), possibly already containing text.

## 4. Output specification

No return value. Exactly the characters described above are appended to `dest`.

## 5. Edge cases and constraints

| `n` | appended text |
|---|---|
| 0 | `00` |
| 3 | `03` |
| 9 | `09` |
| 10 | `10` |
| 23 | `23` |
| 99 | `99` |
| 100 | `100` |
| 1234 | `1234` |
| -5 | `-5` |
| -42 | `-42` |

The function is called several times per logged line, so it must be fast and must not allocate beyond what the buffer itself needs.
