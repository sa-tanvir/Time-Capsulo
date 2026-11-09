def __init__(self, name=None, invoke_without_command=False,
             no_args_is_help=None, subcommand_metavar=None,
             chain=False, result_callback=None, **attrs):
    Command.__init__(self, name, **attrs)
    if no_args_is_help is None:
        no_args_is_help = not invoke_without_command
    self.no_args_is_help = no_args_is_help
    self.invoke_without_command = invoke_without_command
    if subcommand_metavar is None:
        if chain:
            subcommand_metavar = SUBCOMMANDS_METAVAR
        else:
            subcommand_metavar = SUBCOMMAND_METAVAR
    self.subcommand_metavar = subcommand_metavar
    self.chain = chain
    #: The result callback that is stored.  This can be set or
    #: overridden with the :func:`resultcallback` decorator.
    self.result_callback = result_callback

    if self.chain:
        for param in self.params:
            if isinstance(param, Argument) and not param.required:
                raise RuntimeError('Multi commands in chain mode cannot '
                                   'have optional arguments.')
