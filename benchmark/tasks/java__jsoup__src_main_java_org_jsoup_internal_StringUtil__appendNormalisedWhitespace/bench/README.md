Each line: stripLeading flag (0/1), TAB, the input string in a backslash-escaped ASCII encoding (\t \n \f \r \\ \uXXXX per UTF-16 unit). Strings mix letters, whitespace of all kinds, NBSP, zero-width/soft-hyphen characters and supplementary code points; S has 17 hand-made edge cases, M/L have strings of 3,000 / 250,000 chars.
The driver calls StringUtil.appendNormalisedWhitespace(sb, s, flag) on a reused StringBuilder (check mode prefixes the output with '#').
TCBench.java is in the target's package, compiled against target/classes into /tmp/tcb; /w is never modified.
