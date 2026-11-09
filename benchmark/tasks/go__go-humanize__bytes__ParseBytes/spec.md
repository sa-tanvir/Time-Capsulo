# Functional specification: `func ParseBytes(s string) (uint64, error)`

## 1. Component overview

`ParseBytes` is part of the `humanize` package (`github.com/dustin/go-humanize`).
It is the inverse of `Bytes` / `IBytes`: it parses a human-readable size such
as `"42 MB"`, `"42MiB"` or `"1,005.03 MB"` into a number of bytes. Both SI
units (powers of 1000: kB, MB, …) and IEC units (powers of 1024: KiB, MiB, …)
are accepted, up to exabytes.

## 2. Functional requirements

The input is read as a **numeric prefix** followed by a **unit**.

1. **Numeric prefix.** The numeric prefix is the longest leading run of
   characters that are decimal digits, `.` or `,`. It ends at the first
   character that is none of these (for example a space, a letter, `-`,
   `+`). Commas inside it are thousands separators and are ignored wherever
   they appear (`"1,005.03"` means `1005.03`, `"1,0.5k"` means `10.5k`).
2. **Number.** After removing the commas, the prefix must be a valid decimal
   number for `strconv.ParseFloat(…, 64)`: digits with at most one `.`, e.g.
   `"42"`, `"42.5"`, `"5."`, `".5"`, `"007"`. It is converted to the nearest
   `float64`. If it is empty or invalid (e.g. `""`, `"."`, `"1.2.3"`), return
   `0` and the error produced by `strconv.ParseFloat`.
3. **Unit.** The rest of the string, after removing leading and trailing
   white space and converting to lower case, must be one of these unit names
   (case-insensitive in the input):

   | unit (any case) | multiplier |
   |---|---|
   | `""` (no unit), `"b"` | 1 |
   | `"k"`, `"kb"` | 1000 |
   | `"ki"`, `"kib"` | 1024 |
   | `"m"`, `"mb"` | 1000^2 |
   | `"mi"`, `"mib"` | 1024^2 |
   | `"g"`, `"gb"` | 1000^3 |
   | `"gi"`, `"gib"` | 1024^3 |
   | `"t"`, `"tb"` | 1000^4 |
   | `"ti"`, `"tib"` | 1024^4 |
   | `"p"`, `"pb"` | 1000^5 |
   | `"pi"`, `"pib"` | 1024^5 |
   | `"e"`, `"eb"` | 1000^6 |
   | `"ei"`, `"eib"` | 1024^6 |

   (This is the `bytesSizeTable` in the context.) Any other unit text is an
   error: return `0` and an error whose message is
   `"unhandled size name: "` followed by the trimmed, lower-cased unit text
   (e.g. `"84 JB"` gives `unhandled size name: jb`).
4. **Result.** Multiply the parsed `float64` by the unit multiplier (as
   `float64` arithmetic). If the product is greater than or equal to
   `math.MaxUint64` (as a `float64`, i.e. `2^64`), return `0` and an error
   with message `"too large: "` followed by the original input `s`.
   Otherwise return the product converted to `uint64` (fractional bytes are
   truncated toward zero) and a nil error.
5. **Error precedence.** The number is checked first: when both the number
   and the unit are invalid (e.g. `"1.2.3 JB"`, `"JB"`, `" 42 JB"`), the
   `strconv.ParseFloat` error is returned, not the unit error. The
   `too large` check only applies once both are valid.
6. The function is pure and safe for concurrent use.

Examples (all return a nil error):

| input | result |
|---|---|
| `"42"` | `42` |
| `"42MB"`, `"42mb"`, `"42 MB"`, `"42 M"`, `"42m"` | `42000000` |
| `"42MiB"`, `"42mib"`, `"42MIB"`, `"42 MiB"`, `"42Mi"`, `"42 MI"` | `44040192` |
| `"42.5MB"`, `"42.5 M"` | `42500000` |
| `"42.5MiB"`, `"42.5 Mi"` | `44564480` |
| `"1,005.03 MB"` | `1005030000` |
| `"42 kB "` | `42000` |
| `"3 \tk"` | `3000` |
| `"12.5 EB"`, `"12.5 E"` | `12500000000000000000` |
| `"12.5 EiB"` | `uint64(12.5 * float64(1<<60))` = `14411518807585587200` |
| `"0.9"`, `".5"` | `0` |
| `"1.9999999"` | `1` |

Error examples: `"84 JB"` (unknown unit), `""` (no number), `"  42"`
(leading space, so the numeric prefix is empty), `"-5"`, `"1.2.3"`,
`"1e3"` (unit `"e3"` is unknown), `"1 bytes"`, `"16 EiB"` (too large: the
product equals `2^64`), `"18446744073709551615"` (too large: it rounds to
`2^64` as a `float64`).

## 3. Input specification

- `s`: any string. Typical inputs are ASCII; white space between the number
  and the unit, and after the unit, is allowed.

## 4. Output specification

- On success: the number of bytes as `uint64`, and `nil`.
- On failure: `0` and a non-nil `error` (number syntax error from
  `strconv.ParseFloat`, `unhandled size name: <unit>`, or `too large: <s>`).
  The value returned with an error is always `0`.

## 5. Edge cases and constraints

- Leading white space or a sign before the number is not accepted (the
  numeric prefix is then empty, so number parsing fails).
- A string with only commas (`","`) has an empty number after removing the
  commas and is an error.
- Exponent notation is not supported (`"1e3"` is an error, see above).
- Precision is that of `float64`: large values are rounded before the
  conversion to `uint64`.
- The function never panics.
