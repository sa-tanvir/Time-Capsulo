Workload: 60 seeded cases per size: a dict of up to 10 (S) / 100 (M) / 1000 (L) cookie names drawn from a shared pool
(5% None), an optional pre-filled jar (none / RequestsCookieJar / plain http.cookiejar.CookieJar, up to as many
cookies on mixed domains/paths), and overwrite True/False/default. Jars are rebuilt untimed every repeat. The driver
calls `cookiejar_from_dict(d, jar[, overwrite])` and hashes whether the passed jar was returned plus the sorted jar contents.
