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
	var i int
	var key, value Result
	found := false
	for ; i < len(json); i++ {
		if json[i] == '{' {
			i++
			key.Type = String
			obj = true
			found = true
			break
		} else if json[i] == '[' {
			i++
			found = true
			break
		}
		if json[i] > ' ' {
			return
		}
	}
	if !found {
		return
	}
	var str string
	var vesc bool
	var ok bool
	for ; i < len(json); i++ {
		if obj {
			if json[i] != '"' {
				continue
			}
			ks := i
			i, str, vesc, ok = parseString(json, i+1)
			if !ok {
				return
			}
			if vesc {
				key.Str = unescape(str[1 : len(str)-1])
			} else {
				key.Str = str[1 : len(str)-1]
			}
			key.Raw = str
			key.Index = ks
		}
		for ; i < len(json); i++ {
			c := json[i]
			if c == '"' || c == '-' || (c >= '0' && c <= '9') ||
				c == 't' || c == 'f' || c == 'n' || c == '{' || c == '[' {
				break
			}
		}
		if i >= len(json) {
			return
		}
		vs := i
		i, value, ok = parseAny(json, i, true)
		if !ok {
			return
		}
		value.Index = vs
		if !iterator(key, value) {
			return
		}
	}
}
```
