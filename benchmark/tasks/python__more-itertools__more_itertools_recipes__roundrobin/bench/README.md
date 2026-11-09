Workload: seeded cases, each a list of input lengths (0-8 / 40 / 200 inputs for S/M/L, up to 500 / 8k / 20k
total items), with even, random and heavily skewed length distributions so inputs run out at different times.
Input j holds the ints j*10^6 + 0..len-1. Check mode feeds one-shot iterators and hashes repr() of the output;
time mode passes the prebuilt lists directly.
