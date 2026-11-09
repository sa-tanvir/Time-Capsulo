#!/usr/bin/env python3
"""usage: tc-doctest2junit <doctest.xml> <junit.xml> <prefix>
Convert a doctest (2.3.x) XML report into minimal JUnit XML. Test case ids are '<prefix>.<suite>::<name>'.
A case fails if it has failed asserts or an <Exception>, or if the report was cut off inside it (crash).
Truncated reports are parsed incrementally, keeping every completed case."""
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

src, dst, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
cases, suite, cur = [], "", None
try:
    for ev, el in ET.iterparse(src, events=("start", "end")):
        if ev == "start" and el.tag == "TestSuite":
            suite = el.get("name", "")
        elif ev == "start" and el.tag == "TestCase":
            cur = [el.get("name", ""), suite, False, False]   # name, suite, failed, finished
        elif ev == "end" and cur is not None and el.tag == "Exception":
            cur[2] = True
        elif ev == "end" and cur is not None and el.tag == "OverallResultsAsserts":
            if int(el.get("failures", "0")) > 0:
                cur[2] = True
        elif ev == "end" and el.tag == "TestCase" and cur is not None:
            cur[3] = True
            cases.append(cur)
            cur = None
except (ET.ParseError, FileNotFoundError):
    pass
if cur is not None:      # crashed inside this case
    cur[2] = True
    cases.append(cur)
with open(dst, "w") as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<testsuites><testsuite name=%s>\n' % quoteattr(prefix))
    for name, s, failed, _ in cases:
        fh.write('  <testcase classname=%s name=%s>%s</testcase>\n' % (
            quoteattr(prefix + ("." + s if s else "")), quoteattr(name), "<failure/>" if failed else ""))
    fh.write("</testsuite></testsuites>\n")
