```go
func (t Result) arrayOrMap(vc byte, valueize bool) (r arrayOrMapResult) {
	var json = t.Raw
	var i int
	var value Result
	var count int
	var key Result
	if vc == 0 {
		for ; i < len(json); i++ {
			if json[i] == '{' || json[i] == '[' {
				r.vc = json[i]
				i++
				break
			}
			if json[i] > ' ' {
				goto end
			}
		}
	} else {
		for ; i < len(json); i++ {
			if json[i] == vc {
				i++
				break
			}
			if json[i] > ' ' {
				goto end
			}
		}
		r.vc = vc
	}
	if r.vc == '{' {
		if valueize {
			r.oi = make(map[string]interface{})
		} else {
			r.o = make(map[string]Result)
		}
	} else {
		if valueize {
			r.ai = make([]interface{}, 0)
		} else {
			r.a = make([]Result, 0)
		}
	}
	for i < len(json) {
		c := json[i]
		if c <= ' ' {
			i++
			continue
		}
		if c == ']' || c == '}' {
			break
		}
		switch {
		case (c >= '0' && c <= '9') || c == '-':
			value = Result{Type: Number}
			value.Raw, value.Num = tonum(json[i:])
		case c == '{' || c == '[':
			value = Result{Type: JSON}
			value.Raw = squash(json[i:])
		case c == '"':
			value = Result{Type: String}
			value.Raw, value.Str = tostr(json[i:])
		case c == 't':
			value = Result{Type: True}
			value.Raw = tolit(json[i:])
		case c == 'f':
			value = Result{Type: False}
			value.Raw = tolit(json[i:])
		case c == 'n':
			value = Result{Type: Null}
			value.Raw = tolit(json[i:])
		default:
			i++
			continue
		}
		if len(value.Raw) > 0 {
			i += len(value.Raw)
		} else {
			i++
		}
		if r.vc == '{' {
			if count%2 == 0 {
				key = value
			} else {
				if valueize {
					if _, ok := r.oi[key.Str]; !ok {
						r.oi[key.Str] = value.Value()
					}
				} else {
					if _, ok := r.o[key.Str]; !ok {
						r.o[key.Str] = value
					}
				}
			}
			count++
		} else {
			if valueize {
				r.ai = append(r.ai, value.Value())
			} else {
				r.a = append(r.a, value)
			}
		}
	}
	return r
end:
	return arrayOrMapResult{}
}
```
