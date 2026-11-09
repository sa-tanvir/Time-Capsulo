```java
public String consumeToIgnoreCase(String seq) {
    final int start = pos;
    final int seqLen = seq.length();
    final int limit = queue.length() - seqLen;
    int p = start;
    while (p <= limit && !queue.regionMatches(true, p, seq, 0, seqLen)) {
        p++;
    }
    pos = (p <= limit) ? p : queue.length();
    return queue.substring(start, pos);
}
```
