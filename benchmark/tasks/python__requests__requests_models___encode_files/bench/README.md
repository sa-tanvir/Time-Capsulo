Workload: 60 seeded cases per size; each has up to 4/40/400 (S/M/L) form fields (str/bytes names; str, bytes, int,
None or list values) and 1-3/10/30 file entries (bare objects or 2/3/4-tuples/lists) whose content is bytes, str,
bytearray, an unnamed or named BytesIO, an int or None, up to 400 B / 4 KB / 40 KB (content derived in the driver from a seed).
~6% of cases trigger the two ValueErrors. Inputs (fresh streams) are rebuilt outside the timed region each repeat.
The driver calls `RequestEncodingMixin._encode_files(files, data)` and hashes the body and content type with the random
multipart boundary replaced by a constant.
