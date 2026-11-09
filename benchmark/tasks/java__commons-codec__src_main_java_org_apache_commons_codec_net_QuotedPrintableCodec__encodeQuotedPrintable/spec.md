# Functional specification

## 1. Component overview

`QuotedPrintableCodec.encodeQuotedPrintable(BitSet printable, byte[] bytes, boolean strict)` encodes bytes in the Quoted-Printable transfer encoding of RFC 1521 (MIME). Bytes in the "printable" set are written as they are; all other bytes are written as an escape `=` followed by two upper-case hexadecimal digits. In strict mode the output additionally follows the RFC's line-length and white-space rules by inserting soft line breaks.

## 2. Functional requirements

1. If `bytes` is `null`, return `null`.
2. If `printable` is `null`, use the codec's default printable set `PRINTABLE_CHARS` (see context).
3. Every input byte is treated as an unsigned value 0..255 (`b < 0` becomes `256 + b`), and "is printable" means `printable.get(value)`.
4. **Non-strict mode** (`strict == false`): each byte that is in the printable set is copied; each other byte is replaced by `=XY` (`X`, `Y` the upper-case hex digits of the unsigned value, e.g. `=0D`, `=C3`). No line breaks are inserted. Return the resulting bytes.
5. **Strict mode** (`strict == true`), for input of at least three bytes. The output is built with a running column counter `pos`, starting at 1. Let `n` be the length of the input.
   - For each of the first `n - 3` bytes, in order:
     - if `pos < SAFE_LENGTH` (73): write the byte (escaped when it is not printable) and add the number of bytes written (1 or 3) to `pos`;
     - otherwise (the line is full): write the byte, escaped if it is not printable **or** is a blank (space or tab); then write a soft line break (`=` CR LF; the three bytes `=`, `\r`, `\n`) and reset `pos` to 1.
   - The third byte from the end is written escaped if it is not printable, or if it is a blank and `pos > SAFE_LENGTH - 5`; `pos` increases by the bytes written.
   - If now `pos > SAFE_LENGTH - 2`, write a soft line break (`=` CR LF).
   - The last two bytes are each written escaped if they are not printable, or, for the **final** byte only, if it is a blank (space or tab). The second-to-last byte is only escaped if it is not printable.
   - Return the resulting bytes.
6. Strict mode with fewer than three input bytes is outside the contract (the reference fails with an `ArrayIndexOutOfBoundsException`, since it reads the third byte from the end); it need not be supported.

## 3. Input specification

- `printable`: a `BitSet` over 0..255 or `null`.
- `bytes`: any byte array or `null`.
- `strict`: boolean.

## 4. Output specification

A new byte array containing the encoded ASCII text, or `null` when `bytes` is `null`. Examples (non-strict, default set): `"Hello=World"` bytes -> `Hello=3DWorld`; bytes `{0x41, 0x0D, 0x0A, 0xC3}` -> `A=0D=0A=C3`; empty array -> empty array.

## 5. Edge cases and constraints

- The inputs are not modified. Output uses upper-case hex digits only.
- A byte in a custom `printable` set is never escaped (in non-strict mode); in particular `=` is escaped only if it is not in the set.
