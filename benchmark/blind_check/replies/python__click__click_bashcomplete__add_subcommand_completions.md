```python
def add_subcommand_completions(ctx, incomplete, completions_out):
    # Add subcommand completions.
    if isinstance(ctx.command, MultiCommand):
        completions_out.extend(
            [
                (c.name, c.get_short_help_str())
                for c in get_visible_commands_starting_with(ctx, incomplete)
            ]
        )

    # Walk up the context list and add any other completion
    # possibilities from chained commands
    parent_ctx = ctx.parent
    while parent_ctx is not None:
        if isinstance(parent_ctx.command, MultiCommand) and parent_ctx.command.chain:
            protected = parent_ctx.protected_args
            completions_out.extend(
                [
                    (c.name, c.get_short_help_str())
                    for c in get_visible_commands_starting_with(parent_ctx, incomplete)
                    if c.name not in protected
                ]
            )
        parent_ctx = parent_ctx.parent
```
