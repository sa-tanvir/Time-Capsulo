```python
def _match_short_opt(self, arg, state):
    stop = False
    i = 1
    prefix = arg[0]
    unknown_options = []

    for ch in arg[1:]:
        opt = normalize_opt(prefix + ch, self.ctx)
        option = self._short_opt.get(opt)
        i += 1

        if not option:
            if self.ignore_unknown_options:
                unknown_options.append(ch)
                continue
            raise NoSuchOption(opt, ctx=self.ctx)

        if option.takes_value:
            nargs = option.nargs
            rargs = state.rargs
            values = []
            if i < len(arg):
                values.append(arg[i:])
                stop = True
            needed = nargs - len(values)
            if len(rargs) < needed:
                _error_opt_args(nargs, opt)
            if needed > 0:
                values.extend(rargs[:needed])
                del rargs[:needed]
            if nargs == 1:
                value = values[0]
            else:
                value = tuple(values)
        else:
            value = None

        option.process(value, state)

        if stop:
            break

    if self.ignore_unknown_options and unknown_options:
        state.largs.append(prefix + ''.join(unknown_options))
```
