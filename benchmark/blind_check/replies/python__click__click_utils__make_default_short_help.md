```python
def make_default_short_help(help, max_length=45):
    words = help.split()
    total_length = 0
    result = []
    done = False

    for word in words:
        if word[-1:] == '.':
            done = True
        new_length = total_length + len(word) + (1 if result else 0)
        if new_length > max_length:
            result.append('...')
            done = True
        else:
            if result:
                result.append(' ')
            result.append(word)
            total_length = new_length
        if done:
            break

    return ''.join(result)
```
