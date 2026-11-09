basic_json::erase(pos): same workload shape as the range overload, single-element erases.
Driver compiled with g++ -O2 -std=c++11 -fno-access-control -I/w/include, binary cached in /build/drv/<md5 of include/**/*.hpp + driver>; /w is never written.
Workloads are seeded by gen_workload.py (fixed seeds 20191111+i); inputs are within the contract of the function (see spec).
