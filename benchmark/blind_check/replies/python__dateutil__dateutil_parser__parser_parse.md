```python
def _parse(self, timestr, dayfirst=None, yearfirst=None, fuzzy=False,
           fuzzy_with_tokens=False):
    if fuzzy_with_tokens:
        fuzzy = True

    info = self.info

    if dayfirst is None:
        dayfirst = info.dayfirst

    if yearfirst is None:
        yearfirst = info.yearfirst

    res = self._result()
    l = _timelex.split(timestr)  # TypeError propagates

    skipped_idxs = []

    ymd = _ymd()

    len_l = len(l)
    i = 0
    try:
        while i < len_l:
            token = l[i]

            # Check if it's a number
            try:
                float(token)
                is_number = True
            except ValueError:
                is_number = False

            if is_number:
                i = self._parse_numeric_token(l, i, info, ymd, res, fuzzy)

            # Check weekday
            elif info.weekday(token) is not None:
                res.weekday = info.weekday(token)

            # Check month name
            elif info.month(token) is not None:
                ymd.append(info.month(token), 'M')

                if i + 1 < len_l:
                    if l[i + 1] in ('-', '/'):
                        # Jan-01[-99]
                        sep = l[i + 1]
                        ymd.append(l[i + 2])

                        if i + 3 < len_l and l[i + 3] == sep:
                            # Jan-01-99
                            ymd.append(l[i + 4])
                            i += 2

                        i += 2

                    elif (i + 4 < len_l and l[i + 1] == ' ' and
                          l[i + 3] == ' ' and info.pertain(l[i + 2])):
                        # Jan of 01
                        value_repr = l[i + 4]
                        if value_repr.isdigit():
                            year = info.convertyear(int(value_repr))
                            ymd.append(year, 'Y')
                        i += 4

            # Check am/pm
            elif info.ampm(token) is not None:
                value = info.ampm(token)
                val_is_ampm = self._ampm_valid(res.hour, res.ampm, fuzzy)

                if val_is_ampm:
                    res.hour = self._adjust_ampm(res.hour, value)
                    res.ampm = value
                elif fuzzy:
                    skipped_idxs.append(i)

            # Check for a timezone name
            elif self._could_be_tzname(res.hour, res.tzname, res.tzoffset,
                                       token):
                res.tzname = token
                res.tzoffset = info.tzoffset(res.tzname)

                # Check for something like GMT+3, or BRST+3. Notice
                # that it doesn't mean "I am 3 hours after GMT", but
                # "my time +3 is GMT".
                if i + 1 < len_l and l[i + 1] in ('+', '-'):
                    l[i + 1] = '-' if l[i + 1] == '+' else '+'
                    res.tzoffset = None
                    if info.utczone(res.tzname):
                        res.tzname = None

            # Check for a numbered timezone
            elif res.hour is not None and token in ('+', '-'):
                signal = 1 if token == '+' else -1
                offset_repr = l[i + 1]
                len_li = len(offset_repr)

                if len_li == 4:
                    # -0300
                    hour_offset = int(offset_repr[:2])
                    min_offset = int(offset_repr[2:])
                elif i + 2 < len_l and l[i + 2] == ':':
                    # -03:00
                    hour_offset = int(offset_repr)
                    min_offset = int(l[i + 3])
                    i += 2
                elif len_li <= 2:
                    # -[0]3
                    hour_offset = int(offset_repr)
                    min_offset = 0
                else:
                    raise ValueError(timestr)

                res.tzoffset = signal * (hour_offset * 3600 + min_offset * 60)

                # Look for a timezone name between parenthesis
                if (i + 5 < len_l and
                        info.jump(l[i + 2]) and l[i + 3] == '(' and
                        l[i + 5] == ')' and
                        3 <= len(l[i + 4]) and
                        self._could_be_tzname(res.hour, res.tzname,
                                              None, l[i + 4])):
                    # -0300 (BRST)
                    res.tzname = l[i + 4]
                    i += 4

                i += 1

            # Check jumps
            elif info.jump(token) or fuzzy:
                skipped_idxs.append(i)

            else:
                raise ValueError(timestr)

            i += 1

        # Process year/month/day
        year, month, day = ymd.resolve_ymd(yearfirst, dayfirst)

        res.century_specified = ymd.century_specified
        res.year = year
        res.month = month
        res.day = day

    except (IndexError, ValueError):
        return None, None

    if not info.validate(res):
        return None, None

    if fuzzy_with_tokens:
        skipped_tokens = self._recombine_skipped(l, skipped_idxs)
        return res, tuple(skipped_tokens)
    else:
        return res, None
```
