```go
func parseArrayPath(path string) (r arrayPathResult) {
	for i := 0; i < len(path); i++ {
		if path[i] == '|' {
			r.part = path[:i]
			r.pipe = path[i+1:]
			r.piped = true
			return
		}
		if path[i] == '.' {
			r.part = path[:i]
			r.path = path[i+1:]
			r.more = true
			return
		}
		if path[i] == '#' {
			r.arrch = true
			if i == 0 && len(path) > 1 {
				if path[1] == '.' {
					r.alogok = true
					r.alogkey = path[2:]
				} else if path[1] == '(' || path[1] == '[' {
					r.query.on = true
					qpath, op, value, _, fi, ok := parseQuery(path)
					if !ok {
						// bad query, end now
						break
					}
					r.query.path = qpath
					r.query.op = op
					r.query.value = value
					i = fi - 1
					if fi < len(path) && path[fi] == '#' {
						r.query.all = true
					}
				}
			}
			continue
		}
	}
	r.part = path
	r.path = ""
	return
}
```
