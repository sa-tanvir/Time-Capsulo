# Functional specification: `parse_header_links(value)`

## 1. Component overview

A helper in `requests.utils` that parses the value of an HTTP `Link` header
(RFC 5988 style), e.g.
`<http:/.../front.jpeg>; rel=front; type="image/jpeg",<http://.../back.jpeg>; rel=back;type="image/jpeg"`,
into a list of dictionaries, one per link. It is used by `Response.links`.
The parser is deliberately lenient and simple; its exact splitting rules
below define the expected output.

## 2. Functional requirements

Let *Q* be the character set `{' ', "'", '"'}` (space, single quote, double
quote).

1. Strip all leading and trailing characters in *Q* from the whole `value`.
   If the result is empty, return `[]`.
2. Split the stripped value into link entries at every occurrence of a comma
   followed by zero or more spaces and then `<` (the regular expression
   `', *<'`). The matched text (including the `<`) is removed. Commas not
   followed by optional spaces and `<` do not split (so a comma inside a
   parameter value such as `title="a, b"` is kept).
3. For each entry, in order:
   - Split it at the **first** `;` into a URL part and a parameter part. If
     there is no `;`, the whole entry is the URL part and there are no
     parameters.
   - The link's `'url'` is the URL part with all leading/trailing
     characters among `<`, `>`, space, `'` and `"` removed.
   - Split the parameter part on every `;` and process the pieces in order.
     Each piece must contain exactly one `=`; the text before it (stripped
     of *Q* characters) is the key and the text after it (stripped of *Q*
     characters) is the value, stored as `link[key] = value` (a repeated
     key overwrites the earlier value but keeps its original position).
     As soon as a piece does **not** contain exactly one `=` (no `=`, an
     empty piece, or two or more `=`), stop processing the remaining
     parameters of this link (they are ignored); the link itself is still
     kept.
4. Return the list of link dicts in entry order. Each dict has `'url'` as its
   first key, followed by the parameters in order of first appearance.

## 3. Input specification

- `value`: `str`, the raw header value (may be empty).

## 4. Output specification

A `list` of `dict`s mapping `str` to `str`.

| value | result |
|---|---|
| `'<http:/.../front.jpeg>; rel=front; type="image/jpeg"'` | `[{'url': 'http:/.../front.jpeg', 'rel': 'front', 'type': 'image/jpeg'}]` |
| `'<http:/.../front.jpeg>'` | `[{'url': 'http:/.../front.jpeg'}]` |
| `'<http:/.../front.jpeg>;'` | `[{'url': 'http:/.../front.jpeg'}]` |
| `'<http:/.../front.jpeg>; type="image/jpeg",<http://.../back.jpeg>;'` | `[{'url': 'http:/.../front.jpeg', 'type': 'image/jpeg'}, {'url': 'http://.../back.jpeg'}]` |
| `''` | `[]` |
| `'<a>; rel=x;; type=y'` | `[{'url': 'a', 'rel': 'x'}]` (empty piece stops parsing) |
| `'<a>; q=a=b; rel=x'` | `[{'url': 'a'}]` |
| `'<a>; rel=next,   <b>; rel=last'` | `[{'url': 'a', 'rel': 'next'}, {'url': 'b', 'rel': 'last'}]` |

## 5. Edge cases and constraints

- Keys and values may become empty strings after stripping
  (`'<a>; =x'` → `{'url': 'a', '': 'x'}`).
- Whitespace other than spaces (tabs, newlines) is not stripped.
- No URL validation or unquoting is performed.
- Pure function: no side effects; never raises for any `str` input.
