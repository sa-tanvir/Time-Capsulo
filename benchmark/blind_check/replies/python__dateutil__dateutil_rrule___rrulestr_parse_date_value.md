```python
def _parse_date_value(self, date_value, parms, rule_tzids,
                      ignoretz, tzids, tzinfos):
    global parser
    if not parser:
        from dateutil import parser

    datevals = []
    value_found = False
    TZID = None

    for parm in parms:
        if parm.startswith("TZID="):
            try:
                tzkey = rule_tzids[parm.split('TZID=')[-1]]
            except KeyError:
                continue
            if tzids is None:
                from . import tz
                tzlookup = tz.gettz
            elif callable(tzids):
                tzlookup = tzids
            else:
                tzlookup = getattr(tzids, 'get', None)
                if tzlookup is None:
                    msg = ('tzids must be a callable, mapping, or None, '
                           'not %s' % tzids)
                    raise ValueError(msg)

            TZID = tzlookup(tzkey)
            continue

        # RFC 5445 3.8.2.4: The VALUE parameter is optional, but may be found
        # only once.
        if parm not in {"VALUE=DATE-TIME", "VALUE=DATE"}:
            raise ValueError("unsupported parm: " + parm)
        else:
            if value_found:
                msg = ("Duplicate value parameter found in: " + parm)
                raise ValueError(msg)
            value_found = True

    for datestr in date_value.split(','):
        date = parser.parse(datestr, ignoretz=ignoretz, tzinfos=tzinfos)
        if TZID is not None:
            if date.tzinfo is None:
                date = date.replace(tzinfo=TZID)
            else:
                raise ValueError('DTSTART/EXDATE specifies multiple timezone')
        datevals.append(date)

    return datevals
```
