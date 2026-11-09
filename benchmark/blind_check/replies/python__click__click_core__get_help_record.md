```python
def get_help_record(self, ctx):
    if self.hidden:
        return None
    any_prefix_is_slash = []

    def _write_opts(opts):
        rv, any_slashes = join_options(opts)
        if any_slashes:
            any_prefix_is_slash[:] = [True]
        if not self.is_flag and not self.count:
            rv += ' ' + self.make_metavar()
        return rv

    rv = [_write_opts(self.opts)]
    if self.secondary_opts:
        rv.append(_write_opts(self.secondary_opts))

    help = self.help or ''
    extra = []
    if self.show_envvar:
        envvar = self.envvar
        if envvar is None:
            if self.allow_from_autoenv and \
               ctx.auto_envvar_prefix is not None:
                envvar = '%s_%s' % (ctx.auto_envvar_prefix,
                                    self.name.upper())
        if envvar is not None:
            extra.append('env var: %s' % (
                ', '.join('%s' % d for d in envvar)
                if isinstance(envvar, (list, tuple))
                else envvar, ))
    if self.default is not None and self.show_default:
        if isinstance(self.show_default, string_types):
            default_string = '(%s)' % (self.show_default,)
        elif isinstance(self.default, (list, tuple)):
            default_string = ', '.join('%s' % d for d in self.default)
        elif inspect.isfunction(self.default):
            default_string = '(dynamic)'
        else:
            default_string = '%s' % (self.default,)
        extra.append('default: %s' % (default_string,))

    if self.required:
        extra.append('required')
    if extra:
        help = '%s%s[%s]' % (help and help + '  ' or '', '', '; '.join(extra))

    return ((any_prefix_is_slash and '; ' or ' / ').join(rv), help)
```
