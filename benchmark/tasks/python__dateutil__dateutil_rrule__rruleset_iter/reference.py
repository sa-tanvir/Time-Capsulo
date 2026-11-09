def _iter(self):
    rlist = []
    self._rdate.sort()
    self._genitem(rlist, iter(self._rdate))
    for gen in [iter(x) for x in self._rrule]:
        self._genitem(rlist, gen)
    exlist = []
    self._exdate.sort()
    self._genitem(exlist, iter(self._exdate))
    for gen in [iter(x) for x in self._exrule]:
        self._genitem(exlist, gen)
    lastdt = None
    total = 0
    heapq.heapify(rlist)
    heapq.heapify(exlist)
    while rlist:
        ritem = rlist[0]
        if not lastdt or lastdt != ritem.dt:
            while exlist and exlist[0] < ritem:
                exitem = exlist[0]
                advance_iterator(exitem)
                if exlist and exlist[0] is exitem:
                    heapq.heapreplace(exlist, exitem)
            if not exlist or ritem != exlist[0]:
                total += 1
                yield ritem.dt
            lastdt = ritem.dt
        advance_iterator(ritem)
        if rlist and rlist[0] is ritem:
            heapq.heapreplace(rlist, ritem)
    self._len = total
