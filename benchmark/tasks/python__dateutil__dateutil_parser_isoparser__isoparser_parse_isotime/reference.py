def _parse_isotime(self, timestr):
    len_str = len(timestr)
    components = [0, 0, 0, 0, None]
    pos = 0
    comp = -1

    if len(timestr) < 2:
        raise ValueError('ISO time too short')

    has_sep = len_str >= 3 and timestr[2:3] == self._TIME_SEP

    while pos < len_str and comp < 5:
        comp += 1

        if timestr[pos:pos + 1] in b'-+Zz':
            # Detect time zone boundary
            components[-1] = self._parse_tzstr(timestr[pos:])
            pos = len_str
            break

        if comp < 3:
            # Hour, minute, second
            components[comp] = int(timestr[pos:pos + 2])
            pos += 2
            if (has_sep and pos < len_str and
                    timestr[pos:pos + 1] == self._TIME_SEP):
                pos += 1

        if comp == 3:
            # Fraction of a second
            frac = self._FRACTION_REGEX.match(timestr[pos:])
            if not frac:
                continue

            us_str = frac.group(1)[:6]  # Truncate to microseconds
            components[comp] = int(us_str) * 10**(6 - len(us_str))
            pos += len(frac.group())

    if pos < len_str:
        raise ValueError('Unused components in ISO string')

    if components[0] == 24:
        # Standard supports 00:00 and 24:00 as representations of midnight
        if any(component != 0 for component in components[1:4]):
            raise ValueError('Hour may only be 24 at 24:00:00.000')

    return components
