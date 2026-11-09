# Context for the function to implement

- **Language:** python
- **File:** `requests/hooks.py`

## Imports / includes available in this file

```
(none)
```

## Other functions defined in the same file (signatures only; you may call them)

```
default_hooks( )
```

## Module-level constants

```
HOOKS = ['response']          # list of str: the hook event names requests knows about
default_hooks()               # returns {'response': []}, i.e. {event: [] for event in HOOKS}
```

In requests, `dispatch_hook('response', request.hooks, response, **kwargs)` is called after a
response arrives; `request.hooks` maps event names to lists of callables (users may also pass a
single callable instead of a list).
