```python
def invoke(self, ctx):
    def _process_result(value):
        if self.result_callback is not None:
            value = ctx.invoke(self.result_callback, value, **ctx.params)
        return value

    if not ctx.protected_args:
        if self.invoke_without_command:
            if not self.chain:
                return Command.invoke(self, ctx)
            with ctx:
                Command.invoke(self, ctx)
                return _process_result([])
        ctx.fail('Missing command.')

    args = ctx.protected_args + ctx.args
    ctx.args = []
    ctx.protected_args = []

    if not self.chain:
        with ctx:
            cmd_name, cmd, args = self.resolve_command(ctx, args)
            ctx.invoked_subcommand = cmd_name
            Command.invoke(self, ctx)
            sub_ctx = cmd.make_context(cmd_name, args, parent=ctx)
            with sub_ctx:
                return _process_result(sub_ctx.command.invoke(sub_ctx))

    with ctx:
        ctx.invoked_subcommand = args and '*' or None
        Command.invoke(self, ctx)

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
```
