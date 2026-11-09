# Functional specification: `merge_setting(request_setting, session_setting, dict_class=OrderedDict)`

## 1. Component overview

A module-level helper of `requests.sessions`. A `Session` carries default
settings (headers, query params, auth, proxies, `verify`, `stream`, `cert`,
hooks, ...), and each request may supply its own value for the same setting.
`merge_setting` decides the effective value: request values take precedence;
when both values are mappings they are merged key by key, and a request may
delete a session key by setting it to `None`. In a merged result, every key
whose value is `None` is dropped, whichever side (session or request) it
came from.

## 2. Functional requirements

1. If `session_setting` is `None`, return `request_setting` itself (the same
   object, which may also be `None`).
2. Otherwise, if `request_setting` is `None`, return `session_setting`
   itself (same object).
3. Otherwise, if either value is not a `Mapping` (`collections.abc.Mapping`,
   available as `Mapping`), return `request_setting` itself
   (e.g. `merge_setting(False, True)` → `False`;
   `merge_setting(('u', 'p'), {'a': 1})` → `('u', 'p')`).
4. Otherwise build a **new** mapping of type `dict_class`:
   - Start from the session's items, in the session mapping's iteration
     order.
   - Then apply the request's items, in its iteration order, as an update:
     keys already present get the request's value (keeping their original
     position for order-preserving classes); new keys are appended after
     the session keys.
   - Finally remove every key whose resulting value is `None`. This removes
     session entries that the request explicitly sets to `None`, and also
     `None`-valued entries coming from the session mapping itself.
   - Key equality is that of `dict_class`: with the default `OrderedDict`
     keys are case-sensitive (`{'foo': 'bar'}` from the session and
     `{'FOO': 'bar'}` from the request both survive), whereas with
     `dict_class=CaseInsensitiveDict` (used for headers) keys match
     case-insensitively and the request's spelling of a key wins
     (session `{'foo': 'bar'}`, request `{'FOO': None}` → empty result).
   - `dict_class` is called with a list of `(key, value)` pairs, and the
     result is updated with another list of pairs (both `dict`-like
     constructors/`update` accept that).
5. Return the merged mapping.

## 3. Input specification

- `request_setting`: any value or `None`; usually a mapping (headers,
  params, proxies, hooks) or a scalar (`bool`, tuple, string).
- `session_setting`: same kinds of values.
- `dict_class`: a mapping class constructible from a list of pairs and
  supporting `update`, `items` and `del` (default `OrderedDict`; also
  `CaseInsensitiveDict` or `dict`).

## 4. Output specification

Either one of the input objects unchanged (cases 1–3) or a new
`dict_class` instance (case 4).

Example (headers): session `OrderedDict(Accept-Encoding='identity',
First='1', Second='2')`, request `OrderedDict(Third='3', Fourth='4',
Fifth='5', Second='222')` with `dict_class=CaseInsensitiveDict` → items in
order: `Accept-Encoding: identity`, `First: 1`, `Second: 222`, `Third: 3`,
`Fourth: 4`, `Fifth: 5`.

Example (hooks): session `{'response': [h2]}`, request
`{'response': [h1]}` → `{'response': [h1]}` (values are replaced, not
combined).

Example: session `{'Accept-Encoding': None, 'X': '1'}`, request `{}` →
`{'X': '1'}`.

## 5. Edge cases and constraints

- Neither input is mutated.
- Values are not copied (the merged mapping holds the same value objects).
- Two empty mappings yield an empty `dict_class` instance.
- `to_key_val_list` (from `.utils`) converts a mapping into a list of its
  `(key, value)` items and may be used.
