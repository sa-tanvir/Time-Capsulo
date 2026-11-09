# Functional specification: `read_varu32(data: &[u8]) -> (u32, usize)`

## 1. Component overview

Internal helper of the `regex` crate's lazy DFA. DFA states are stored compactly as byte strings in which
instruction pointers are written as variable-length integers (the LEB128 / Protocol Buffers "varint"
format, produced by the sibling `write_varu32`). `read_varu32` decodes **one** unsigned varint from the
start of `data` and reports how many bytes it occupied. It is called for every instruction pointer each
time a DFA state is expanded, so it is on a hot path of almost every regex search.

## 2. Functional requirements

1. A varint is a sequence of bytes in which every byte except the last has its high bit (`0x80`) set; the
   first byte whose high bit is clear terminates it.
2. The value is assembled little-endian, 7 bits per byte: the low 7 bits of byte `i` (0-based) contribute
   `(byte_i & 0x7F) << (7 * i)`.
3. Return `(value, k)` where `k` is the number of bytes consumed, i.e. the index of the terminating byte
   plus one. Bytes after the terminator are ignored.
4. If `data` contains no terminating byte (empty input, or every byte has the high bit set), return
   `(0, 0)`.
5. Redundant (non-minimal) encodings are accepted: e.g. `[0x80, 0x00]` decodes to `(0, 2)` and
   `[0x81, 0x80, 0x00]` to `(1, 3)`.

Examples:

| `data` (hex) | result |
|---|---|
| `00` | `(0, 1)` |
| `01` | `(1, 1)` |
| `7f` | `(127, 1)` |
| `80 01` | `(128, 2)` |
| `ac 02` | `(300, 2)` |
| `ff ff 03` | `(65535, 3)` |
| `ff ff ff 7f` | `(268435455, 4)` |
| `ff ff ff ff 0f` | `(4294967295, 5)` |
| `0a 0b` | `(10, 1)` |
| `96 01 02 03` | `(150, 2)` |
| (empty) | `(0, 0)` |
| `80`, `ff ff ff ff` | `(0, 0)` |

Property (tested): for every `n: u32`, writing `n` with `write_varu32` into an empty buffer and reading it
back yields `(n, buffer.len())`. The signed variant `read_vari32` relies on this function and must
round-trip every `i32` as well.

## 3. Input specification

- `data: &[u8]`: any length. Inputs in this crate always encode a value that fits in `u32`, so a
  terminated varint never has more than 5 bytes; longer encodings do not occur and need not be handled.

## 4. Output specification

- `(u32, usize)`: decoded value and number of bytes consumed (1–5), or `(0, 0)` if unterminated.

## 5. Edge cases and constraints

- Pure function; no allocation; no mutation; must not read past the terminating byte or past `data`.
- Typically called in a loop that advances through a buffer by the returned length until it gets 0.
