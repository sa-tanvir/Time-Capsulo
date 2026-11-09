# Functional specification: `func ParseBigBytes(s string) (*big.Int, error)`

## 1. Component overview

`ParseBigBytes` is part of the `humanize` package (`github.com/dustin/go-humanize`).
It is the arbitrary-precision inverse of `BigBytes` / `BigIBytes`: it parses
a human-readable size such as `"42 MB"`, `"16.5 ZiB"` or `"1,005.03 MB"` into
an exact number of bytes as a `*big.Int` (from `math/big`). Both SI units
(powers of 1000) and IEC units (powers of 1024) are accepted, up to
yottabytes, and the result is never limited to 64 bits.

## 2. Functional requirements

The input is read as a **numeric prefix** followed by a **unit**.

1. **Numeric prefix.** The numeric prefix is the longest leading run of
   characters that are decimal digits, `.` or `,`. It ends at the first
   character that is none of these (a space, a letter, `-`, `+`, …). Commas
   in it are thousands separators and are ignored wherever they appear
   (`"1,005.03"` means `1005.03`, `"1,,2"` means `12`).
2. **Number.** After removing the commas, the prefix must be a decimal
   number made of digits with at most one `.` and at least one digit, e.g.
   `"42"`, `"42.5"`, `"5."`, `".5"`, `"007"`. Its value is taken **exactly**
   (as a rational number, with no floating-point rounding, however many
   digits it has). If it is empty or malformed (`""`, `"."`, `"1.2.3"`),
   return `nil` and a non-nil error.
3. **Unit.** The rest of the string, with leading and trailing white space
   removed and converted to lower case, must be one of:

   | unit (any case) | multiplier |
   |---|---|
   | `""` (no unit), `"b"` | 1 |
   | `"k"`, `"kb"` / `"ki"`, `"kib"` | 1000 / 1024 |
   | `"m"`, `"mb"` / `"mi"`, `"mib"` | 1000^2 / 1024^2 |
   | `"g"`, `"gb"` / `"gi"`, `"gib"` | 1000^3 / 1024^3 |
   | `"t"`, `"tb"` / `"ti"`, `"tib"` | 1000^4 / 1024^4 |
   | `"p"`, `"pb"` / `"pi"`, `"pib"` | 1000^5 / 1024^5 |
   | `"e"`, `"eb"` / `"ei"`, `"eib"` | 1000^6 / 1024^6 |
   | `"z"`, `"zb"` / `"zi"`, `"zib"` | 1000^7 / 1024^7 |
   | `"y"`, `"yb"` / `"yi"`, `"yib"` | 1000^8 / 1024^8 |

   (These are the entries of `bigBytesSizeTable` in the context.) Any other
   unit text is an error: return `nil` and an error whose message is
   `"unhandled size name: "` followed by the trimmed, lower-cased unit text
   (e.g. `"84 JB"` gives `unhandled size name: jb`).
4. **Result.** Multiply the exact number by the unit multiplier and return
   the largest integer not greater than the product (fractional bytes are
   dropped), as a newly allocated `*big.Int`, with a nil error. There is no
   upper limit.
5. **Error precedence.** The number is checked first: when both the number
   and the unit are invalid (e.g. `"1.2.3 JB"`, `"JB"`, `" 42 JB"`), the
   number error is returned (not `unhandled size name: ...`).
6. The function does not modify any package-level value (in particular the
   multiplier values must stay unchanged) and is safe for concurrent use.

Examples (all with a nil error):

| input | result |
|---|---|
| `"42"` | `42` |
| `"42MB"`, `"42mb"`, `"42 MB"`, `"42 M"`, `"42m"` | `42000000` |
| `"42MiB"`, `"42mib"`, `"42MIB"`, `"42 Mi"`, `"42 MI"` | `44040192` |
| `"42.5MB"`, `"42.5 M"` | `42500000` |
| `"42.5MiB"`, `"42.5 Mi"` | `44564480` |
| `"1,005.03 MB"` | `1005030000` |
| `"12.5 EB"`, `"12.5 E"` | `12500000000000000000` |
| `"12.5 EiB"` | `14411518807585587200` |
| `"16 EiB"` | `18446744073709551616` |
| `"15.99 EiB"` | `18435214858663483146` |
| `"16 ZB"`, `"16 Z"` | `16000000000000000000000` |
| `"16 ZiB"`, `"16 Zi"` | `18889465931478580854784` |
| `"16.5 ZiB"` | `19479761741837286506496` |
| `"16 YiB"` | `19342813113834066795298816` |
| `"16.5 YiB"`, `"16.5 Yi"` | `19947276023641381382651904` |
| `"0.9"`, `".5"` | `0` |
| `"1.9999999"` | `1` |
| `"3 \tk"` | `3000` |

Error examples: `"84 JB"`, `""`, `"  42"` (leading space: empty numeric
prefix), `"-5"`, `"."`, `"1.2.3"`, `"1e3"` (unit `"e3"`), `"1 bytes"`.

## 3. Input specification

- `s`: any string. Inputs are ASCII. White space between the number and the
  unit, and after the unit, is allowed. The number may have many digits
  (hundreds or more) in its integer or fractional part.

## 4. Output specification

- On success: a non-nil `*big.Int` holding the byte count (always `>= 0`),
  and `nil`.
- On failure: `nil` and a non-nil `error`.

## 5. Edge cases and constraints

- Leading white space or a sign before the number makes the numeric prefix
  empty, which is an error.
- Exponent notation is not supported (`"1e3"` is an error).
- Results beyond 64 bits are exact (`"16 EiB"` is `2^64`, not an error).
- Long fractional parts are exact: `"0.000000000000000000001 YB"` is `1000`.
- The function never panics.
