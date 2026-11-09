```python
def get_token(self):
    if self.tokenstack:
        return self.tokenstack.pop(0)

    seenletters = False
    token = None
    state = None

    while self.charstack or not self.eof:
        if self.charstack:
            nextchar = self.charstack.pop(0)
        else:
            nextchar = self.instream.read(1)
            while nextchar == '\x00':
                nextchar = self.instream.read(1)

        if not nextchar:
            self.eof = True
            break
        elif not state:
            # First character of the token decides its kind
            token = nextchar
            if self.isword(nextchar):
                state = 'a'
            elif self.isnum(nextchar):
                state = '0'
            elif self.isspace(nextchar):
                token = ' '
                break
            else:
                break
        elif state == 'a':
            # Word
            seenletters = True
            if self.isword(nextchar):
                token += nextchar
            elif nextchar == '.':
                token += nextchar
                state = 'a.'
            else:
                self.charstack.append(nextchar)
                break
        elif state == '0':
            # Number
            if self.isnum(nextchar):
                token += nextchar
            elif nextchar == '.' or (nextchar == ',' and len(token) >= 2):
                token += nextchar
                state = '0.'
            else:
                self.charstack.append(nextchar)
                break
        elif state == 'a.':
            # Dotted chunk, letter phase
            seenletters = True
            if nextchar == '.' or self.isword(nextchar):
                token += nextchar
            elif self.isnum(nextchar) and token[-1] == '.':
                token += nextchar
                state = '0.'
            else:
                self.charstack.append(nextchar)
                break
        elif state == '0.':
            # Dotted chunk, digit phase
            if nextchar == '.' or self.isnum(nextchar):
                token += nextchar
            elif self.isword(nextchar) and token[-1] == '.':
                token += nextchar
                state = 'a.'
            else:
                self.charstack.append(nextchar)
                break

    if (state in ('a.', '0.') and (seenletters or token.count('.') > 1 or
                                   token[-1] in '.,')):
        pieces = self._split_decimal.split(token)
        token = pieces[0]
        for tok in pieces[1:]:
            if tok:
                self.tokenstack.append(tok)

    if state == '0.' and token.count('.') == 0:
        token = token.replace(',', '.')

    return token
```
