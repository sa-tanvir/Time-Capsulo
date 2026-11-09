Workload: seeded lists of ints, short strings, small (unhashable) lists and mixed hashable/unhashable
values with varying duplicate ratios; keys are None, str.lower, tuple, or x % 97.
Unhashable cases are kept shorter (S: 60, M: 300, L: 800 items) than hashable ones (S: 400, M: 6k, L: 60k).
The driver passes a one-shot iterator and consumes the whole result; check mode hashes repr() of each output.
