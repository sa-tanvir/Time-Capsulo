Workload: 60 seeded cases per size. Target is a RequestsCookieJar, a plain http.cookiejar.CookieJar or (rarely) a dict
(ValueError path); source is a dict, a RequestsCookieJar, a plain CookieJar or None. Each side holds up to 10 (S) /
100 (M) / 1000 (L) cookies from a shared name pool on mixed domains/paths. Inputs are rebuilt untimed every repeat.
The driver calls `merge_cookies(target, src)` and hashes identity of the result plus its sorted cookie contents.
