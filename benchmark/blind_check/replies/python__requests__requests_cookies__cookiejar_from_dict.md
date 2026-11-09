```python
def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True):
    if cookiejar is None:
        cookiejar = RequestsCookieJar()

    if cookie_dict is not None:
        if overwrite:
            names_from_jar = ()
        else:
            names_from_jar = {cookie.name for cookie in cookiejar}
        for name in cookie_dict:
            if overwrite or (name not in names_from_jar):
                cookiejar.set_cookie(create_cookie(name, cookie_dict[name]))

    return cookiejar
```
