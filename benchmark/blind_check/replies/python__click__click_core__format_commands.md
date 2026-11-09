```python
def format_commands(self, ctx, formatter):
    commands = []
    for subcommand in self.list_commands(ctx):
        cmd = self.get_command(ctx, subcommand)
        if cmd is None:
            continue
        if cmd.hidden:
            continue
        commands.append((subcommand, cmd))

    if commands:
        limit = formatter.width - 6 - max(len(name) for name, _ in commands)
        rows = []
        for subcommand, cmd in commands:
            rows.append((subcommand, cmd.get_short_help_str(limit)))
        with formatter.section('Commands'):
            formatter.write_dl(rows)
```
