```python
def resolve_ymd(self, yearfirst, dayfirst):
    len_ymd = len(self)
    year, month, day = (None, None, None)

    strids = (('y', self.ystridx),
              ('m', self.mstridx),
              ('d', self.dstridx))

    strids = {key: val for key, val in strids if val is not None}
    if (len_ymd == len(strids) > 0 or
            (len_ymd == 3 and len(strids) == 2)):
        return self._resolve_from_stridxs(strids)

    mstridx = self.mstridx

    if len_ymd > 3:
        raise ValueError("More than three YMD values")
    elif len_ymd == 1 or (mstridx is not None and len_ymd == 2):
        # One member, or two members with a month string
        if mstridx is not None:
            month = self[mstridx]
            other = self[1 - mstridx] if len_ymd == 2 else None
        else:
            other = self[0]

        if other is not None:
            if other > 31:
                year = other
            else:
                day = other

    elif len_ymd == 2:
        # Two members with numbers
        if self[0] > 31:
            # 99-01
            year, month = self
        elif self[1] > 31:
            # 01-99
            month, year = self
        elif dayfirst and self[1] <= 12:
            # 13-01
            day, month = self
        else:
            # 01-13
            month, day = self

    elif len_ymd == 3:
        # Three members
        if mstridx == 0:
            if self[1] > 31:
                # Apr-2003-25
                month, year, day = self
            else:
                month, day, year = self
        elif mstridx == 1:
            if self[0] > 31 or (yearfirst and self[2] <= 31):
                # 99-Jan-01
                year, month, day = self
            else:
                # 01-Jan-01
                day, month, year = self

        elif mstridx == 2:
            if self[1] > 31:
                # 01-99-Jan
                day, year, month = self
            else:
                # 99-01-Jan
                year, day, month = self

        else:
            if (self[0] > 31 or
                    self.ystridx == 0 or
                    (yearfirst and self[1] <= 12 and self[2] <= 31)):
                # 99-01-01
                if dayfirst and self[2] <= 12:
                    year, day, month = self
                else:
                    year, month, day = self
            elif self[0] > 12 or (dayfirst and self[1] <= 12):
                # 13-01-01
                day, month, year = self
            else:
                # 01-13-01
                month, day, year = self

    return year, month, day
```
