basic_json::erase(first,last): arrays/objects with many sequential range erases (iterators of object members are pre-collected in the untimed reset step), plus S edge cases (primitives, null, foreign iterators). Hash = final document + returned positions/keys + exception messages.
Driver compiled with g++ -O2 -std=c++11 -fno-access-control -I/w/include, binary cached in /build/drv/<md5 of include/**/*.hpp + driver>; /w is never written.
Workloads are seeded by gen_workload.py (fixed seeds 20191111+i); inputs are within the contract of the function (see spec).
