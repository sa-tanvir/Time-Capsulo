def _parse_rfc(self, s):
    lines = s.splitlines()
    if not lines:
        raise ValueError("empty string")

    # Unfold
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            del lines[i]
        elif i > 0 and line[0] == " ":
            lines[i-1] += line[1:]
            del lines[i]
        else:
            i += 1

    tzid = None
    comps = []
    invtz = False
    comptype = None
    for line in lines:
        if not line:
            continue
        name, value = line.split(':', 1)
        parms = name.split(';')
        if not parms:
            raise ValueError("empty property name")
        name = parms[0].upper()
        parms = parms[1:]
        if invtz:
            if name == "BEGIN":
                if value in ("STANDARD", "DAYLIGHT"):
                    # Process component
                    pass
                else:
                    raise ValueError("unknown component: "+value)
                comptype = value
                founddtstart = False
                tzoffsetfrom = None
                tzoffsetto = None
                rrulelines = []
                tzname = None
            elif name == "END":
                if value == "VTIMEZONE":
                    if comptype:
                        raise ValueError("component not closed: "+comptype)
                    if not tzid:
                        raise ValueError("mandatory TZID not found")
                    if not comps:
                        raise ValueError(
                            "at least one component is needed")
                    # Process vtimezone
                    self._vtz[tzid] = _tzicalvtz(tzid, comps)
                    invtz = False
                elif value == comptype:
                    if not founddtstart:
                        raise ValueError("mandatory DTSTART not found")
                    if tzoffsetfrom is None:
                        raise ValueError(
                            "mandatory TZOFFSETFROM not found")
                    if tzoffsetto is None:
                        raise ValueError(
                            "mandatory TZOFFSETFROM not found")
                    # Process component
                    rr = None
                    if rrulelines:
                        rr = rrule.rrulestr("\n".join(rrulelines),
                                            compatible=True,
                                            ignoretz=True,
                                            cache=True)
                    comp = _tzicalvtzcomp(tzoffsetfrom, tzoffsetto,
                                          (comptype == "DAYLIGHT"),
                                          tzname, rr)
                    comps.append(comp)
                    comptype = None
                else:
                    raise ValueError("invalid component end: "+value)
            elif comptype:
                if name == "DTSTART":
                    # DTSTART in VTIMEZONE takes a subset of valid RRULE
                    # values under RFC 5545.
                    for parm in parms:
                        if parm != 'VALUE=DATE-TIME':
                            msg = ('Unsupported DTSTART param in ' +
                                   'VTIMEZONE: ' + parm)
                            raise ValueError(msg)
                    rrulelines.append(line)
                    founddtstart = True
                elif name in ("RRULE", "RDATE", "EXRULE", "EXDATE"):
                    rrulelines.append(line)
                elif name == "TZOFFSETFROM":
                    if parms:
                        raise ValueError(
                            "unsupported %s parm: %s " % (name, parms[0]))
                    tzoffsetfrom = self._parse_offset(value)
                elif name == "TZOFFSETTO":
                    if parms:
                        raise ValueError(
                            "unsupported TZOFFSETTO parm: "+parms[0])
                    tzoffsetto = self._parse_offset(value)
                elif name == "TZNAME":
                    if parms:
                        raise ValueError(
                            "unsupported TZNAME parm: "+parms[0])
                    tzname = value
                elif name == "COMMENT":
                    pass
                else:
                    raise ValueError("unsupported property: "+name)
            else:
                if name == "TZID":
                    if parms:
                        raise ValueError(
                            "unsupported TZID parm: "+parms[0])
                    tzid = value
                elif name in ("TZURL", "LAST-MODIFIED", "COMMENT"):
                    pass
                else:
                    raise ValueError("unsupported property: "+name)
        elif name == "BEGIN" and value == "VTIMEZONE":
            tzid = None
            comps = []
            invtz = True
