```go
func (t Result) ForEach(iterator func(key, value Result) bool) {
	if !t.Exists() {
		return
	}
	if t.Type != JSON {
		iterator(Result{}, t)
		return
	}
	json := t.Raw
	var obj bool
	i := 0
	for ; i < len(json); i++ {
		if json[i] <= ' ' {
			continue
		}
		if json[i] == '{' {
			obj = true
		} else if json[i] == '[' {
			obj = false
		} else {
			return
		}
		i++
		break
	}
	if i >= len(json) {
		return
	}
	var key, value Result
	var ok bool
	for {
		// skip separators
		for i < len(json) && (json[i] <= ' ' || json[i] == ',' || json[i] == ':') {
			i++
		}
		if i >= len(json) {
			return
		}
		if json[i] == ']' || json[i] == '}' {
			return
		}
		if obj {
			if json[i] != '"' {
				return
			}
			keyIdx := i
			i++
			var raw string
			var escaped bool
			i, raw, escaped, ok = parseString(json, i)
			if !ok {
				return
			}
			key = Result{Type: String, Raw: raw, Index: keyIdx}
			body := raw[1 : len(raw)-1]
			if escaped {
				key.Str = unescape(body)
			} else {
				key.Str = body
			}
			for i < len(json) && (json[i] <= ' ' || json[i] == ':') {
				i++
			}
			if i >= len(json) || json[i] == '}' || json[i] == ']' || json[i] == ',' {
				return
			}
		}
		valIdx := i
		i, value, ok = parseAny(json, i, true)
		if !ok {
			return
		}
		value.Index = valIdx
		if !iterator(key, value) {
			return
		}
	}
}
```
