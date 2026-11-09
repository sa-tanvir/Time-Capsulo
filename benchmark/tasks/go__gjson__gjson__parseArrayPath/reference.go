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
					r.path = path[:1]
				} else if path[1] == '[' || path[1] == '(' {
					// query
					r.query.on = true
					if true {
						qpath, op, value, _, fi, ok := parseQuery(path[i:])
						if !ok {
							// bad query, end now
							break
						}
						r.query.path = qpath
						r.query.op = op
						r.query.value = value
						i = fi - 1
						if i+1 < len(path) && path[i+1] == '#' {
							r.query.all = true
						}
					} else {
						var end byte
						if path[1] == '[' {
							end = ']'
						} else {
							end = ')'
						}
						i += 2
						// whitespace
						for ; i < len(path); i++ {
							if path[i] > ' ' {
								break
							}
						}
						s := i
						for ; i < len(path); i++ {
							if path[i] <= ' ' ||
								path[i] == '!' ||
								path[i] == '=' ||
								path[i] == '<' ||
								path[i] == '>' ||
								path[i] == '%' ||
								path[i] == end {
								break
							}
						}
						r.query.path = path[s:i]
						// whitespace
						for ; i < len(path); i++ {
							if path[i] > ' ' {
								break
							}
						}
						if i < len(path) {
							s = i
							if path[i] == '!' {
								if i < len(path)-1 && (path[i+1] == '=' ||
									path[i+1] == '%') {
									i++
								}
							} else if path[i] == '<' || path[i] == '>' {
								if i < len(path)-1 && path[i+1] == '=' {
									i++
								}
							} else if path[i] == '=' {
								if i < len(path)-1 && path[i+1] == '=' {
									s++
									i++
								}
							}
							i++
							r.query.op = path[s:i]
							// whitespace
							for ; i < len(path); i++ {
								if path[i] > ' ' {
									break
								}
							}
							s = i
							for ; i < len(path); i++ {
								if path[i] == '"' {
									i++
									s2 := i
									for ; i < len(path); i++ {
										if path[i] > '\\' {
											continue
										}
										if path[i] == '"' {
											// look for an escaped slash
											if path[i-1] == '\\' {
												n := 0
												for j := i - 2; j > s2-1; j-- {
													if path[j] != '\\' {
														break
													}
													n++
												}
												if n%2 == 0 {
													continue
												}
											}
											break
										}
									}
								} else if path[i] == end {
									if i+1 < len(path) && path[i+1] == '#' {
										r.query.all = true
									}
									break
								}
							}
							if i > len(path) {
								i = len(path)
							}
							v := path[s:i]
							for len(v) > 0 && v[len(v)-1] <= ' ' {
								v = v[:len(v)-1]
							}
							r.query.value = v
						}
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
