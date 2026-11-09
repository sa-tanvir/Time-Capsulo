def _parse(self, timestr, dayfirst=None, yearfirst=None, fuzzy=False,
           fuzzy_with_tokens=False):
    """
    Private method which performs the heavy lifting of parsing, called from
    ``parse()``, which passes on its ``kwargs`` to this function.

    :param timestr:
        The string to parse.

    :param dayfirst:
        Whether to interpret the first value in an ambiguous 3-integer date
        (e.g. 01/05/09) as the day (``True``) or month (``False``). If
        ``yearfirst`` is set to ``True``, this distinguishes between YDM
        and YMD. If set to ``None``, this value is retrieved from the
        current :class:`parserinfo` object (which itself defaults to
        ``False``).

    :param yearfirst:
        Whether to interpret the first value in an ambiguous 3-integer date
        (e.g. 01/05/09) as the year. If ``True``, the first number is taken
        to be the year, otherwise the last number is taken to be the year.
        If this is set to ``None``, the value is retrieved from the current
        :class:`parserinfo` object (which itself defaults to ``False``).

    :param fuzzy:
        Whether to allow fuzzy parsing, allowing for string like "Today is
        January 1, 2047 at 8:21:00AM".

    :param fuzzy_with_tokens:
        If ``True``, ``fuzzy`` is automatically set to True, and the parser
        will return a tuple where the first element is the parsed
        :class:`datetime.datetime` datetimestamp and the second element is
        a tuple containing the portions of the string which were ignored:

        .. doctest::

            >>> from dateutil.parser import parse
            >>> parse("Today is January 1, 2047 at 8:21:00AM", fuzzy_with_tokens=True)
            (datetime.datetime(2047, 1, 1, 8, 21), (u'Today is ', u' ', u'at '))

    """
    if fuzzy_with_tokens:
        fuzzy = True

    info = self.info

    if dayfirst is None:
        dayfirst = info.dayfirst

    if yearfirst is None:
        yearfirst = info.yearfirst

    res = self._result()
    l = _timelex.split(timestr)         # Splits the timestr into tokens

    skipped_idxs = []

    # year/month/day list
    ymd = _ymd()

    len_l = len(l)
    i = 0
    try:
        while i < len_l:

            # Check if it's a number
            value_repr = l[i]
            try:
                value = float(value_repr)
            except ValueError:
                value = None

            if value is not None:
                # Numeric token
                i = self._parse_numeric_token(l, i, info, ymd, res, fuzzy)

            # Check weekday
            elif info.weekday(l[i]) is not None:
                value = info.weekday(l[i])
                res.weekday = value

            # Check month name
            elif info.month(l[i]) is not None:
                value = info.month(l[i])
                ymd.append(value, 'M')

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

                    elif (i + 4 < len_l and l[i + 1] == l[i + 3] == ' ' and
                          info.pertain(l[i + 2])):
                        # Jan of 01
                        # In this case, 01 is clearly year
                        if l[i + 4].isdigit():
                            # Convert it here to become unambiguous
                            value = int(l[i + 4])
                            year = str(info.convertyear(value))
                            ymd.append(year, 'Y')
                        else:
                            # Wrong guess
                            pass
                            # TODO: not hit in tests
                        i += 4

            # Check am/pm
            elif info.ampm(l[i]) is not None:
                value = info.ampm(l[i])
                val_is_ampm = self._ampm_valid(res.hour, res.ampm, fuzzy)

                if val_is_ampm:
                    res.hour = self._adjust_ampm(res.hour, value)
                    res.ampm = value

                elif fuzzy:
                    skipped_idxs.append(i)

            # Check for a timezone name
            elif self._could_be_tzname(res.hour, res.tzname, res.tzoffset, l[i]):
                res.tzname = l[i]
                res.tzoffset = info.tzoffset(res.tzname)

                # Check for something like GMT+3, or BRST+3. Notice
                # that it doesn't mean "I am 3 hours after GMT", but
                # "my time +3 is GMT". If found, we reverse the
                # logic so that timezone parsing code will get it
                # right.
                if i + 1 < len_l and l[i + 1] in ('+', '-'):
                    l[i + 1] = ('+', '-')[l[i + 1] == '+']
                    res.tzoffset = None
                    if info.utczone(res.tzname):
                        # With something like GMT+3, the timezone
                        # is *not* GMT.
                        res.tzname = None

            # Check for a numbered timezone
            elif res.hour is not None and l[i] in ('+', '-'):
                signal = (-1, 1)[l[i] == '+']
                len_li = len(l[i + 1])

                # TODO: check that l[i + 1] is integer?
                if len_li == 4:
                    # -0300
                    hour_offset = int(l[i + 1][:2])
                    min_offset = int(l[i + 1][2:])
                elif i + 2 < len_l and l[i + 2] == ':':
                    # -03:00
                    hour_offset = int(l[i + 1])
                    min_offset = int(l[i + 3])  # TODO: Check that l[i+3] is minute-like?
                    i += 2
                elif len_li <= 2:
                    # -[0]3
                    hour_offset = int(l[i + 1][:2])
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
            elif not (info.jump(l[i]) or fuzzy):
                raise ValueError(timestr)

            else:
                skipped_idxs.append(i)
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
