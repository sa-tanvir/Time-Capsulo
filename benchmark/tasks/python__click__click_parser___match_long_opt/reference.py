def _match_long_opt(self, opt, explicit_value, state):
    if opt not in self._long_opt:
        possibilities = [word for word in self._long_opt
                         if word.startswith(opt)]
        raise NoSuchOption(opt, possibilities=possibilities, ctx=self.ctx)

    option = self._long_opt[opt]
    if option.takes_value:
        # At this point it's safe to modify rargs by injecting the
        # explicit value, because no exception is raised in this
        # branch.  This means that the inserted value will be fully
        # consumed.
        if explicit_value is not None:
            state.rargs.insert(0, explicit_value)

        nargs = option.nargs
        if len(state.rargs) < nargs:
            _error_opt_args(nargs, opt)
        elif nargs == 1:
            value = state.rargs.pop(0)
        else:
            value = tuple(state.rargs[:nargs])
            del state.rargs[:nargs]

    elif explicit_value is not None:
        raise BadOptionUsage(opt, '%s option does not take a value' % opt)

    else:
        value = None

    option.process(value, state)
