```python
def _parse_rfc(self, s,
               dtstart=None,
               cache=False,
               unfold=False,
               forceset=False,
               compatible=False,
               ignoretz=False,
               tzids=None,
               tzinfos=None):
    global parser
    if compatible:
        forceset = True
        unfold = True

    TZID_NAMES = dict(map(
        lambda x: (x.upper(), x),
        re.findall('TZID=(?P<name>[^:]+):', s)
    ))
    s = s.upper()
    if not s.strip():
        raise ValueError("empty string")
    if unfold:
        lines = s.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line:
                del lines[i]
            elif i > 0 and line[0] == " ":
                lines[i - 1] += line[1:]
                del lines[i]
            else:
                lines[i] = line
                i += 1
    else:
        lines = s.split()
    if (not forceset and len(lines) == 1 and (s.find(':') == -1 or
                                              s.startswith('RRULE:'))):
        return self._parse_rfc_rrule(lines[0], cache=cache,
                                     dtstart=dtstart, ignoretz=ignoretz,
                                     tzinfos=tzinfos)
    else:
        rrulevals = []
        rdatevals = []
        exrulevals = []
        exdatevals = []
        for line in lines:
            if not line:
                continue
            if line.find(':') == -1:
                name = "RRULE"
                value = line
            else:
                name, value = line.split(':', 1)
            parms = name.split(';')
            if not parms:
                raise ValueError("empty property name")
            name = parms[0]
            parms = parms[1:]
            if name == "RRULE":
                for parm in parms:
                    raise ValueError("unsupported RRULE parm: " + parm)
                rrulevals.append(value)
            elif name == "RDATE":
                for parm in parms:
                    if parm != "VALUE=DATE-TIME":
                        raise ValueError("unsupported RDATE parm: " + parm)
                rdatevals.append(value)
            elif name == "EXRULE":
                for parm in parms:
                    raise ValueError("unsupported EXRULE parm: " + parm)
                exrulevals.append(value)
            elif name == "EXDATE":
                exdatevals.extend(
                    self._parse_date_value(value, parms,
                                           TZID_NAMES, ignoretz,
                                           tzids, tzinfos)
                )
            elif name == "DTSTART":
                dtvals = self._parse_date_value(value, parms, TZID_NAMES,
                                                ignoretz, tzids, tzinfos)
                if len(dtvals) != 1:
                    raise ValueError("Multiple DTSTART values specified:" +
                                     value)
                dtstart = dtvals[0]
            else:
                raise ValueError("unsupported property: " + name)
        if (forceset or len(rrulevals) > 1 or rdatevals
                or exrulevals or exdatevals):
            if not parser and (rdatevals or exdatevals):
                from dateutil import parser
            rset = rruleset(cache=cache)
            for value in rrulevals:
                rset.rrule(self._parse_rfc_rrule(value, dtstart=dtstart,
                                                 ignoretz=ignoretz,
                                                 tzinfos=tzinfos))
            for value in rdatevals:
                for datestr in value.split(','):
                    rset.rdate(parser.parse(datestr,
                                            ignoretz=ignoretz,
                                            tzinfos=tzinfos))
            for value in exrulevals:
                rset.exrule(self._parse_rfc_rrule(value, dtstart=dtstart,
                                                  ignoretz=ignoretz,
                                                  tzinfos=tzinfos))
            for value in exdatevals:
                rset.exdate(value)
            if compatible and dtstart:
                rset.rdate(dtstart)
            return rset
        else:
            return self._parse_rfc_rrule(rrulevals[0],
                                         dtstart=dtstart,
                                         cache=cache,
                                         ignoretz=ignoretz,
                                         tzinfos=tzinfos)
```
