def add_subcommand_completions(ctx, incomplete, completions_out):
    # Add subcommand completions.
    if isinstance(ctx.command, MultiCommand):
        completions_out.extend(
            [(c.name, c.get_short_help_str()) for c in get_visible_commands_starting_with(ctx, incomplete)])

    # Walk up the context list and add any other completion possibilities from chained commands
    while ctx.parent is not None:
        ctx = ctx.parent
        if isinstance(ctx.command, MultiCommand) and ctx.command.chain:
            remaining_commands = [c for c in get_visible_commands_starting_with(ctx, incomplete)
                                  if c.name not in ctx.protected_args]
            completions_out.extend([(c.name, c.get_short_help_str()) for c in remaining_commands])
