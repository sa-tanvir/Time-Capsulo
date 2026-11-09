```python
def _find_no_duplicates(self, name, domain=None, path=None):
    found = None
    for cookie in iter(self):
        if cookie.name != name:
            continue
        if domain is not None and cookie.domain != domain:
            continue
        if path is not None and cookie.path != path:
            continue
        if found is not None:
            raise CookieConflictError(
                'There are multiple cookies with name, %r' % (name)
            )
        found = cookie

    if found is not None and found.value:
        return found.value
    raise KeyError('name=%r, domain=%r, path=%r' % (name, domain, path))
```
