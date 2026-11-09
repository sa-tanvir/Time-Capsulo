# Functional specification: `RequestEncodingMixin._encode_files(files, data)`

## 1. Component overview

A static method of `RequestEncodingMixin` (mixed into `PreparedRequest` of the
`requests` HTTP library). It builds a `multipart/form-data` request body from
ordinary form fields (`data`) and file uploads (`files`), and returns the body
together with the matching `Content-Type` header value. The actual multipart
serialisation is delegated to urllib3 (`RequestField`,
`encode_multipart_formdata`, both imported in this module).

## 2. Functional requirements

1. **Validation.**
   - If `files` is falsy (`None`, `{}`, `[]`), raise
     `ValueError("Files must be provided.")`.
   - Else, if `data` is a `str` or `bytes`, raise
     `ValueError("Data must not be a string.")`.
2. **Normalise containers.** Both `data` (or `{}` if `data` is falsy) and
   `files` are turned into ordered lists of `(name, value)` pairs with
   `to_key_val_list` (mappings in iteration order, sequences of pairs in
   their order). An element of `files` that is not a 2-item pair (e.g.
   `files=['bad file data']`) causes a `ValueError` during unpacking.
3. **Plain form fields come first**, in order. For each `(field, val)` of
   `data`:
   - If `val` is a `str`/`bytes` or is not iterable, it is a single value;
     otherwise (list, tuple, ...) each element is a separate value for the
     same field name, in order.
   - `None` values are skipped.
   - A value that is not `bytes` is converted with `str()` first; then `str`
     values are UTF-8 encoded, so every emitted value is `bytes`.
   - A field name given as `bytes` is decoded from UTF-8 to `str`
     (`{b'stuff': 'elixr'}` yields a part named `stuff`, not `b'stuff'`).
   - Each value becomes one simple multipart part, given to
     `encode_multipart_formdata` as a `(name, value_bytes)` tuple (part with
     only a `Content-Disposition: form-data; name="..."` header).
4. **File parts follow**, in order. For each `(k, v)` of `files`:
   - If `v` is a `tuple` or `list`, it is `(filename, fileobj)`,
     `(filename, fileobj, content_type)` or
     `(filename, fileobj, content_type, custom_headers)`; missing items
     default to `None`.
   - Otherwise `v` itself is the file object/content and the filename is
     `guess_filename(v)`, or the key `k` if that gives nothing (e.g. an
     object without a usable `name`, or whose `name` is not a string).
   - Content of the part: if the file object is `str`, `bytes` or
     `bytearray`, it is used directly; if it has a `read` attribute, the
     result of calling `read()` once is used; if it is `None`, the entry is
     skipped entirely (no part at all); any other object (e.g. an `int`) is
     used as-is.
   - Each part is a urllib3 `RequestField` with name `k`, that content, the
     filename and the custom headers, made multipart with the given content
     type (so the part carries `Content-Disposition: form-data; name="k";
     filename="..."` and, when a content type was given, a `Content-Type`
     header, e.g. `text/py-content-type`).
5. **Encode** all parts (form fields first, then files) with
   `encode_multipart_formdata` and return its `(body, content_type)` result.

## 3. Input specification

- `files`: a mapping or a sequence of `(name, value)` pairs. `value` is a
  file-like object, `str`/`bytes`/`bytearray` content, `None`, another
  object, or a 2/3/4-tuple/list as described above. Names are `str`.
- `data`: `None`, a mapping or sequence of `(name, value)` pairs (names
  `str` or `bytes`; values `str`, `bytes`, numbers, `None` or lists of
  these). Must not be a `str`/`bytes`.

## 4. Output specification

A 2-tuple `(body, content_type)`:
- `body`: `bytes`, the complete multipart body.
- `content_type`: `str` of the form
  `'multipart/form-data; boundary=<boundary>'`. The boundary is randomly
  chosen by urllib3; callers must not rely on its value.

Example: `files={'file': ('report.csv', b'a,b\n', 'text/csv')}`,
`data={'k': ['1', 2], 'skip': None}` produces a body with three parts in
order: `name="k"` / `1`, `name="k"` / `2`, then
`name="file"; filename="report.csv"` with `Content-Type: text/csv` and
content `a,b\n`.

`files={"random-file-1": None, "random-file-2": 1}`: the body has no part
named `random-file-1` and one part named `random-file-2` (filename
`random-file-2`, content `1`).

## 5. Edge cases and constraints

- File-like objects are read (consumed) exactly once; nothing else is
  mutated.
- A file object whose `name` attribute is a non-string (e.g. `2`) or looks
  like `<stdin>` falls back to the key as filename.
- Field values given as `bytes` are passed through without re-encoding.
- Errors: only the two `ValueError`s above plus whatever unpacking or
  urllib3 raises for malformed inputs.
