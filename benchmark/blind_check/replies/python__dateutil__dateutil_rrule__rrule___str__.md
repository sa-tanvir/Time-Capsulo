```python
def __str__(self):
    output = []
    if self._dtstart:
        output.append(self._dtstart.strftime('DTSTART:%Y%m%dT%H%M%S'))

    parts = ['FREQ=' + FREQNAMES[self._freq]]
    if self._interval != 1:
        parts.append('INTERVAL=' + str(self._interval))

    day_codes = ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU')
    if self._wkst:
        parts.append('WKST=' + day_codes[self._wkst])

    if self._count is not None:
        parts.append('COUNT=' + str(self._count))

    if self._until:
        parts.append(self._until.strftime('UNTIL=%Y%m%dT%H%M%S'))

    original_rule = self._original_rule
    for name, key in (('BYSETPOS', 'bysetpos'),
                      ('BYMONTH', 'bymonth'),
                      ('BYMONTHDAY', 'bymonthday'),
                      ('BYYEARDAY', 'byyearday'),
                      ('BYWEEKNO', 'byweekno'),
                      ('BYDAY', 'byweekday'),
                      ('BYHOUR', 'byhour'),
                      ('BYMINUTE', 'byminute'),
                      ('BYSECOND', 'bysecond'),
                      ('BYEASTER', 'byeaster')):
        value = original_rule.get(key)
        if not value:
            continue
        if key == 'byweekday':
            items = []
            for wday in value:
                code = day_codes[wday.weekday]
                if wday.n:
                    items.append('%+d%s' % (wday.n, code))
                else:
                    items.append(code)
        else:
            items = [str(v) for v in value]
        parts.append('%s=%s' % (name, ','.join(items)))

    output.append('RRULE:' + ';'.join(parts))
    return '\n'.join(output)
```
