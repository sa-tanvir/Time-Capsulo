Each line: three flags (inAttribute, normaliseWhite, stripLeadingWhite), charset (UTF-8/US-ASCII/ISO-8859-1), escape mode (base/xhtml/extended) and an escaped string with markup characters, NBSP, accented, CJK and supplementary characters and whitespace. S/M/L: 40 / 3,000 / 250,000 chars per case.
The driver calls the package-private Entities.escape(StringBuilder, ...) from TCBench in package org.jsoup.nodes; OutputSettings objects are prepared once per charset/mode.
TCBench.java is in the target's package, compiled against target/classes into /tmp/tcb; /w is never modified.
