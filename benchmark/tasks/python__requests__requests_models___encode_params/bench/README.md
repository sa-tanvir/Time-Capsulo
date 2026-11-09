Workload: 100 seeded cases per size. Most are ordered dicts, lists of pairs or tuples of pairs with up to
10 (S) / 100 (M) / 1000 (L) entries; keys are str or bytes, values str (incl. non-ASCII and reserved characters),
bytes, ints, floats, None, or lists of these. ~10% are pass-through inputs (raw str/bytes, None, int).
The driver calls `RequestEncodingMixin._encode_params(data)` and hashes `repr()` of each result.
