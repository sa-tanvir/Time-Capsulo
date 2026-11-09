```python
def is_incomplete_option(all_args, cmd_param):
    if not isinstance(cmd_param, Option):
        return False
    if cmd_param.is_flag:
        return False
    nargs = cmd_param.nargs
    if not nargs or nargs <= 0:
        return False
    words = [arg for arg in all_args if arg != "="]
    if not words:
        return False
    window = words[-nargs:]
    for word in window:
        if word.startswith("-"):
            return word in cmd_param.opts
    return False
```
