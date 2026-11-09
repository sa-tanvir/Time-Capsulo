# Functional specification: `scoped_pad(wrapped_size, padinfo, dest)` (constructor)

## 1. Component overview

`scoped_pad` is a small RAII helper of spdlog's pattern formatter. A formatter creates a `scoped_pad` for a field of known length, then appends the field text to the buffer, and lets the object go out of scope. The constructor writes the padding that must come before the text and records how many padding characters must come after it; the destructor writes those. The result is that the field occupies at least `padinfo.width_` characters, aligned according to `padinfo.side_`.

## 2. Functional requirements

Let `width = padinfo.width_`, `side = padinfo.side_` and `n = wrapped_size` (the number of characters the caller is going to append after construction).

1. If `width <= n`, no padding is needed: nothing is appended to `dest` and nothing is left for the destructor.
2. Otherwise let `total = width - n`:
   - `side == left`: append `total` spaces to `dest` now; nothing is left for the destructor (the text ends up right-aligned).
   - `side == right`: append nothing now; the destructor has to append `total` spaces (the text ends up left-aligned).
   - `side == center`: append `total / 2` spaces (integer division, rounded down) now; the destructor has to append the remaining `total - total / 2` spaces (so when `total` is odd, the extra space goes on the right).
3. The number of spaces the destructor appends is held in the member that the destructor reads (see the instance state); every path through the constructor must leave it set to the correct value, including 0.

The constructor only appends spaces (`' '`) to `dest`; it does not read or modify anything already in `dest`. It does not modify `padinfo`.

## 3. Input specification

- `wrapped_size`: `size_t`, from 0 to a few thousand.
- `padinfo`: a `padding_info` with `width_` between 0 and 128 and `side_` one of `left`, `right`, `center`.
- `dest`: a `fmt::memory_buffer` that may already contain text.

## 4. Output specification

No return value. After the constructor, `dest` has the leading padding appended; after the whole object's lifetime (constructor, caller's text, destructor) the buffer holds `[leading spaces][text][trailing spaces]`.

## 5. Edge cases and constraints

| width | side | n | leading spaces (constructor) | trailing spaces (destructor) |
|---|---|---|---|---|
| 8 | left | 4 | 4 | 0 |
| 8 | right | 4 | 0 | 4 |
| 8 | center | 4 | 2 | 2 |
| 7 | center | 2 | 2 | 3 |
| 3 | left | 14 | 0 | 0 |
| 4 | center | 4 | 0 | 0 |
| 0 | any | 0 | 0 | 0 |
| 5 | center | 0 | 2 | 3 |

The constructor is invoked for every padded field of every log line, so it must be cheap.
