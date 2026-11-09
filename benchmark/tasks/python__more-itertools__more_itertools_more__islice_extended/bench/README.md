Workload: seeded random slices over integer sequences (S: up to 100 items, M: 2k, L: 20k),
mixing 1/2/3-argument forms, None bounds, negative/out-of-range start/stop and steps in {±1,2,3,7,-2,-5}.
The driver passes a fresh one-shot iterator (`iter(list)`) per call and fully consumes the result;
check mode hashes repr() of every output list.
