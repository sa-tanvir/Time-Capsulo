def make_default_short_help(help, max_length=45):
    """Return a condensed version of help string."""
    words = help.split()
    total_length = 0
    result = []
    done = False

    for word in words:
        if word[-1:] == '.':
            done = True
        new_length = result and 1 + len(word) or len(word)
        if total_length + new_length > max_length:
            result.append('...')
            done = True
        else:
            if result:
                result.append(' ')
            result.append(word)
        if done:
            break
        total_length += new_length

    return ''.join(result)
