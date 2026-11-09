# Functional specification: `RequestEncodingMixin._encode_params(data)`

## 1. Component overview

A static method of `RequestEncodingMixin` (mixed into `PreparedRequest` in the
`requests` HTTP library). It turns request parameters or form data into an
`application/x-www-form-urlencoded` string, used both for URL query strings
and for form-encoded request bodies. Values that are already "raw" are passed
through untouched.

## 2. Functional requirements

1. If `data` is a `str` or `bytes`, return it unchanged (same object).
2. Else, if `data` has a `read` attribute (file-like), return it unchanged.
3. Else, if `data` is iterable (has `__iter__`, e.g. a `dict`, `OrderedDict`,
   other mapping, `list` or `tuple` of 2-item pairs), convert it to a list of
   `(key, value)` pairs with `to_key_val_list(data)` (mappings contribute their
   items in iteration order; sequences of pairs keep their order) and:
   - A value that is a `str`/`bytes`, or that is not iterable (int, float,
     `None`, ...), is treated as a single value. Any other iterable value
     (list, tuple, ...) is treated as a sequence of values for the same key,
     producing one `key=value` entry per element, in order.
   - Individual values that are `None` are dropped (a key whose only value is
     `None`, or whose value list is empty, does not appear at all).
   - Keys and values that are `str` are UTF-8 encoded before quoting; `bytes`
     are used as-is; other objects (numbers, ...) are converted with `str()`.
   - The result is exactly what the standard library's
     `urlencode(pairs, doseq=True)` produces for the flattened, encoded list
     of pairs: entries joined by `&`, key and value joined by `=`, quoted with
     `quote_plus` rules (space → `+`, reserved and non-ASCII bytes →
     upper-case `%XX`, letters, digits and `_.-~` kept).
4. Otherwise (any non-iterable object such as an `int`), return `data`
   unchanged.

## 3. Input specification

- `data`: `str`, `bytes`, a file-like object, a mapping, an iterable of
  2-item `(key, value)` sequences, `None`, or any other object.
- Keys: `str` or `bytes` (or other objects accepted by `urlencode`).
- Values: `str`, `bytes`, numbers, `None`, or lists/tuples of these.

## 4. Output specification

- For iterable input: a `str` (possibly empty `''`).
- Otherwise the input object itself.

Examples:

| data | result |
|---|---|
| `{'life': '42'}` | `'life=42'` |
| `{'test': ['foo', 'baz']}` | `'test=foo&test=baz'` |
| `(('a', 'b'), ('c', 'd'))` | `'a=b&c=d'` |
| `OrderedDict([('z', 1), ('a', 1), ('k', 1), ('d', 1)])` | `'z=1&a=1&k=1&d=1'` |
| `{'foo': 'føø'}` | `'foo=f%C3%B8%C3%B8'` |
| `{'a': 'x y', 'b': None}` | `'a=x+y'` |
| `{b'k': b'v&w'}` | `'k=v%26w'` |
| `[('k', [1, None, 'x'])]` | `'k=1&k=x'` |
| `'already=encoded'` / `b'raw'` | returned unchanged |
| `None` | `None` |
| `{}` / `[]` | `''` |

## 5. Edge cases and constraints

- Must not mutate `data`.
- The output for a list/tuple of pairs is equal to the standard
  `urlencode(data)` when all keys and values are plain ASCII strings
  (tests compare against it).
- A sequence element that is not a 2-item pair makes unpacking fail with
  `ValueError`; no special handling is required.
- Order of the output entries follows the input order exactly.
