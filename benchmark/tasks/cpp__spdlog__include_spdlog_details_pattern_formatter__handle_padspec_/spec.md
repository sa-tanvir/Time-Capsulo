# Functional specification: `pattern_formatter::handle_padspec_(it, end)`

## 1. Component overview

Part of spdlog's pattern formatter. In a log pattern a flag can be preceded by a padding specification, for example `%8l`, `%-8l` or `%=8l` (flag `l` padded to 8 characters on the left, right or centred). When the pattern is compiled, this function parses the padding specification that follows a `%` and tells the caller how far it got.

## 2. Functional requirements

`it` is a reference to an iterator into the pattern string and `end` is the end of the pattern. The function reads the specification starting at `*it` and advances `it` past every character it consumed. The specification has the form `[side][width]`:

1. If `it == end`, the result is a default `padding_info` (width 0, side `left`) and `it` is unchanged.
2. *Side*: if `*it` is `-` the side is `right` and the character is consumed; if `*it` is `=` the side is `center` and the character is consumed; any other character leaves the side `left` and consumes nothing.
3. *Width*: if the iterator is now at `end` or the character at `it` is not a decimal digit (`0`..`9`), there is no width: the result is a `padding_info` with width 0 and the side found in rule 2 (a width of 0 means padding is not enabled), and `it` stays just after whatever was consumed by rule 2.
4. Otherwise all consecutive decimal digits starting at `it` are consumed and read as a decimal number (leading zeros are allowed and do not change the value: `007` is 7). The width is that number, but limited to a maximum of 128 (a larger number gives width 128). The result is a `padding_info` with this width and the side from rule 2.
5. Only the characters described are consumed: after the digits, `it` points at the first character that is not a digit (this is the flag character), which is left unconsumed.

## 3. Input specification

- `it`: `std::string::const_iterator &`, a valid position in `[begin, end]` of the pattern.
- `end`: the end iterator of the same string.
- Numbers that appear in the pattern have a value below 10^18 (arbitrarily many leading zeros are possible); no overflow handling is needed.

## 4. Output specification

Returns `details::padding_info` by value (width 0..128, side `left`, `right` or `center`). `it` is advanced as described. No exceptions are thrown.

## 5. Edge cases and constraints

Examples (the text is what follows the `%`; `it` offset is the number of characters consumed):

| text | result (width, side) | consumed |
|---|---|---|
| (empty) | 0, left | 0 |
| `8l` | 8, left | 1 |
| `-8l` | 8, right | 2 |
| `=8l` | 8, center | 2 |
| `v` | 0, left | 0 |
| `-` | 0, right | 1 |
| `=x` | 0, center | 1 |
| `-x` | 0, right | 1 |
| `128n` | 128, left | 3 |
| `300n` | 128, left | 3 |
| `-300n` | 128, right | 4 |
| `007v` | 7, left | 3 |
| `-=5` | 0, right | 1 |
| `==5v` | 0, center | 1 |
| `12ab34` | 12, left | 2 |

The function is called for every `%` of every pattern; input strings may contain thousands of leading zeros, so it must run in time linear in the characters it consumes.
