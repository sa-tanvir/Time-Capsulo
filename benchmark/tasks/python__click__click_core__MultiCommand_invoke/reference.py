def invoke(self, ctx):
    def _process_result(value):
        if self.result_callback is not None:
            value = ctx.invoke(self.result_callback, value,
                               **ctx.params)
        return value

    if not ctx.protected_args:
        # If we are invoked without command the chain flag controls
        # how this happens.  If we are not in chain mode, the return
        # value here is the return value of the command.
        # If however we are in chain mode, the return value is the
        # return value of the result processor invoked with an empty
        # list (which means that no subcommand actually was executed).
        if self.invoke_without_command:
            if not self.chain:
                return Command.invoke(self, ctx)
            with ctx:
                Command.invoke(self, ctx)
                return _process_result([])
        ctx.fail('Missing command.')

    # Fetch args back out
    args = ctx.protected_args + ctx.args
    ctx.args = []
    ctx.protected_args = []

    # If we're not in chain mode, we only allow the invocation of a
    # single command but we also inform the current context about the
    # name of the command to invoke.
    if not self.chain:
        # Make sure the context is entered so we do not clean up
        # resources until the result processor has worked.
        with ctx:
            cmd_name, cmd, args = self.resolve_command(ctx, args)
            ctx.invoked_subcommand = cmd_name
            Command.invoke(self, ctx)
            sub_ctx = cmd.make_context(cmd_name, args, parent=ctx)
            with sub_ctx:
                return _process_result(sub_ctx.command.invoke(sub_ctx))

    # In chain mode we create the contexts step by step, but after the
    # base command has been invoked.  Because at that point we do not
    # know the subcommands yet, the invoked subcommand attribute is
    # set to ``*`` to inform the command that subcommands are executed
    # but nothing else.
    with ctx:
        ctx.invoked_subcommand = args and '*' or None
        Command.invoke(self, ctx)

        # Otherwise we make every single context and invoke them in a
        # chain.  In that case the return value to the result processor
        # is the list of all invoked subcommand's results.
        contexts = []
        while args:
            cmd_name, cmd, args = self.resolve_command(ctx, args)
            sub_ctx = cmd.make_context(cmd_name, args, parent=ctx,
                                       allow_extra_args=True,
                                       allow_interspersed_args=False)
            contexts.append(sub_ctx)
            args, sub_ctx.args = sub_ctx.args, []

        rv = []
        for sub_ctx in contexts:
            with sub_ctx:
                rv.append(sub_ctx.command.invoke(sub_ctx))
        return _process_result(rv)
