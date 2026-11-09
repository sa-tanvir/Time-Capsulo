# Functional specification: `Request.__init__(self, method=None, url=None, headers=None, files=None, data=None, params=None, auth=None, cookies=None, hooks=None, json=None)`

## 1. Component overview

The constructor of `requests.Request`, the user-facing, not-yet-prepared
description of an HTTP request. It stores the given request components as
attributes, substituting empty containers for omitted ones, and registers
any supplied event hooks. `Request.prepare()` and `Session.prepare_request()`
later read these attributes.

## 2. Functional requirements

1. Store the arguments on the instance under the same names:
   `self.method`, `self.url`, `self.headers`, `self.files`, `self.data`,
   `self.json`, `self.params`, `self.auth`, `self.cookies`.
   - The objects passed in are stored as-is (no copying, no validation, no
     normalisation): e.g. `self.headers is headers` when a headers dict is
     given, and a `bytes` URL stays `bytes`.
   - Defaults when the argument is `None`: `data` → a new empty list `[]`,
     `files` → a new empty list `[]`, `headers` → a new empty dict `{}`,
     `params` → a new empty dict `{}`. Each instance gets its own fresh
     containers. `method`, `url`, `json`, `auth` and `cookies` stay `None`
     when not given.
   - Only `None` triggers a default; other falsy values (e.g. `{}`, `''`)
     are stored unchanged.
2. Hooks:
   - `self.hooks` is always a **new** dict created with `default_hooks()`,
     i.e. `{'response': []}` (one empty list per supported event).
   - If `hooks` is given (a mapping of event name → hook or iterable of
     hooks), each `(event, hook)` item is registered, in the mapping's
     iteration order, through `self.register_hook(event=event, hook=hook)`:
     - a callable is appended to `self.hooks[event]`;
     - an iterable is expanded and its callable elements appended in order
       (non-callables are silently skipped);
     - an event name that is not supported raises
       `ValueError('Unsupported event specified, with event name "<event>"')`.
   - The caller's `hooks` mapping and lists are never stored or mutated:
     `Request(hooks=h).hooks is not h`, and `self.hooks['response']` is a
     different list from any list in `h`.
3. Returns `None` (constructor).

## 3. Input specification

All parameters are optional:
- `method`: `str` (e.g. `'GET'`) or `None`.
- `url`: `str`/`bytes` or `None`.
- `headers`: mapping or `None`.
- `files`, `data`: mapping / list of tuples / `str` / `bytes` / file-like,
  or `None`.
- `params`: mapping, list of tuples, `str`/`bytes`, or `None`.
- `auth`: tuple or auth callable, or `None`.
- `cookies`: dict or `CookieJar`, or `None`.
- `hooks`: mapping of event name to a callable or an iterable of callables,
  or `None`.
- `json`: any JSON-serialisable object or `None`.

## 4. Output specification

No return value; the instance attributes described above are set.

Examples:
- `Request()` → `method=None, url=None, headers={}, files=[], data=[],
  json=None, params={}, auth=None, cookies=None, hooks={'response': []}`.
- `Request('GET', 'http://x/', hooks={'response': h})` →
  `hooks == {'response': [h]}`.
- `Request(hooks={'response': [h1, 'not callable', h2]})` →
  `hooks == {'response': [h1, h2]}`.
- `Request(hooks={'response': []})` → `hooks == {'response': []}`.
- `Request(hooks={'request': h})` → `ValueError`.

## 5. Edge cases and constraints

- The instance must remain picklable (attributes are plain stored objects).
- Registering happens after `self.hooks` has been initialised; other
  attributes may be set before or after hook registration, but if
  registration raises, the exception propagates.
