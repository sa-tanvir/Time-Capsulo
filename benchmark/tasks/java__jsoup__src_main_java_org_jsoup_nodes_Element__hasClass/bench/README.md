Groups of lines: 'E key value' builds a div Element with that class attribute (key spelled class/CLASS/Class, or none), followed by 'Q name' queries asked against it (present names in other case, prefixes/suffixes, absent, empty). S: many short elements; M: 3 attributes of ~3,000 chars; L: 3 attributes of ~300,000 chars.
The driver builds Element(Tag div) and calls hasClass(name).
TCBench.java is in the target's package, compiled against target/classes into /tmp/tcb; /w is never modified.
