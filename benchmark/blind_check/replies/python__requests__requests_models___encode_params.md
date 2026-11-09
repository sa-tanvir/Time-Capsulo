```python
def _encode_params(data):
    if isinstance(data, (str, bytes)):
        return data
    elif hasattr(data, 'read'):
        return data
    elif hasattr(data, '__iter__'):
        result = []
        for k, vs in to_key_val_list(data):
            if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                vs = [vs]
            if isinstance(k, str):
                k = k.encode('utf-8')
            elif not isinstance(k, bytes):
                k = str(k)
            for v in vs:
                if v is None:
                    continue
                if isinstance(v, str):
                    v = v.encode('utf-8')
                elif not isinstance(v, bytes):
                    v = str(v)
                result.append((k, v))
        return urlencode(result, doseq=True)
    else:
        return data
```
