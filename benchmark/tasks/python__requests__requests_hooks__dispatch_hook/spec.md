# Functional specification: `dispatch_hook(key, hooks, hook_data, **kwargs)`

## 1. Component overview

`dispatch_hook` runs the user-registered callbacks ("hooks") for one event of
the requests hook system. Requests calls it with the event name `'response'`,
the hook registry of a request and the freshly received response; each hook may
inspect the data and optionally replace it, and the final value is what the
caller continues with. The function is generic: it works for any event name and
any kind of data.

## 2. Functional requirements

1. Treat a falsy `hooks` argument (`None`, `{}`) as an empty registry.
2. Look up the entry for `key` in the registry with the mapping's `get`
   method. If there is no entry, or the entry is falsy (`None`, `[]`, `()`),
   return `hook_data` unchanged without calling anything.
3. If the entry is itself callable (a function, lambda, bound method or any
   object with a `__call__` attribute), it is the only hook. Otherwise the
   entry is an iterable of callables (list, tuple, ...) and the hooks are taken
   in iteration order.
4. Call the hooks one after another. Each hook receives the *current* data as
   its single positional argument plus all extra keyword arguments given to
   `dispatch_hook` (forwarded unchanged to every hook).
   - If a hook returns a value other than `None`, that value becomes the
     current data for the following hooks and for the final result.
   - If a hook returns `None`, the current data stays as it was (the hook is
     treated as having modified the data in place, or as a pure observer).
5. Return the current data after the last hook.

Examples (with `def hook(value): return value[1:]`):

- `dispatch_hook('response', {'response': hook}, 'Data')` gives `'ata'`.
- `dispatch_hook('response', {'response': [hook, lambda x: None, hook]}, 'Data')`
  gives `'ta'` (the middle hook returns `None` and does not reset the data).
- `dispatch_hook('response', {'response': []}, 'Data')` gives `'Data'`.
- `dispatch_hook('response', None, 'Data')` and
  `dispatch_hook('response', {}, 'Data')` give `'Data'`.
- `dispatch_hook('other', {'response': [hook]}, 'Data')` gives `'Data'`
  (no hooks registered for that key).
- `dispatch_hook('response', {'response': (f,)}, 5, step=2)` with
  `def f(x, step): return x + step` gives `7`.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `key` | hashable (normally `str`, e.g. `'response'`) | Event name to dispatch. |
| `hooks` | mapping (usually `dict`) of key to a callable or an iterable of callables, or `None` | Hook registry. |
| `hook_data` | any object | Initial data passed to the first hook. |
| `**kwargs` | any keyword arguments | Forwarded to every hook call. |

## 4. Output specification

The data after all hooks ran: `hook_data` itself if no hook ran or every hook
returned `None`, otherwise the last non-`None` value returned by a hook. The
registry is not modified; `hook_data` is only modified if a hook mutates it.

## 5. Edge cases and constraints

- A returned value that is falsy but not `None` (`0`, `''`, `[]`, `False`)
  still replaces the data.
- Every hook is called exactly once, in order; there is no short-circuit.
- Exceptions raised by a hook propagate to the caller unchanged; later hooks are
  not called.
- Each hook is called with exactly one positional argument.
- No I/O of its own; thread safety depends only on the hooks.
