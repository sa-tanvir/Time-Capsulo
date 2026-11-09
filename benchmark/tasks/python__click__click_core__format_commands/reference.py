def format_commands(self, ctx, formatter):
    """Extra format methods for multi methods that adds all the commands
    after the options.
    """
    commands = []
    for subcommand in self.list_commands(ctx):
        cmd = self.get_command(ctx, subcommand)
        # What is this, the tool lied about a command.  Ignore it
        if cmd is None:
            continue
        if cmd.hidden:
            continue

        commands.append((subcommand, cmd))

    # allow for 3 times the default spacing
    if len(commands):
        limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

        rows = []
        for subcommand, cmd in commands:
            help = cmd.get_short_help_str(limit)
            rows.append((subcommand, help))

        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)
