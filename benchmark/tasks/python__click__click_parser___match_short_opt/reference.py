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
            # Any characters left in arg?  Pretend they're the
            # next arg, and stop consuming characters of arg.
            if i < len(arg):
                state.rargs.insert(0, arg[i:])
                stop = True

            nargs = option.nargs
            if len(state.rargs) < nargs:
                _error_opt_args(nargs, opt)
            elif nargs == 1:
                value = state.rargs.pop(0)
            else:
                value = tuple(state.rargs[:nargs])
                del state.rargs[:nargs]

        else:
            value = None

        option.process(value, state)

        if stop:
            break

    # If we got any unknown options we re-combinate the string of the
    # remaining options and re-attach the prefix, then report that
    # to the state as new larg.  This way there is basic combinatorics
    # that can be achieved while still ignoring unknown arguments.
    if self.ignore_unknown_options and unknown_options:
        state.largs.append(prefix + ''.join(unknown_options))
