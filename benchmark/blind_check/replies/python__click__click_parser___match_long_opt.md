```python
def _match_long_opt(self, opt, explicit_value, state):
    if opt not in self._long_opt:
        possibilities = [word for word in self._long_opt
                         if word.startswith(opt)]
        raise NoSuchOption(opt, possibilities=possibilities, ctx=self.ctx)

    option = self._long_opt[opt]
    if option.takes_value:
        nargs = option.nargs
        rargs = state.rargs
        available = len(rargs) + (1 if explicit_value is not None else 0)
        if available < nargs:
            _error_opt_args(nargs, opt)
        if explicit_value is not None:
            values = [explicit_value]
            take = nargs - 1
        else:
            values = []
            take = nargs
        if take:
            values.extend(rargs[:take])
            del rargs[:take]
        if nargs == 1:
            value = values[0]
        else:
            value = tuple(values)
    elif explicit_value is not None:
        raise BadOptionUsage(opt, '%s option does not take a value' % opt)
    else:
        value = None

    option.process(value, state)
```
