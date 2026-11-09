basic_json::diff(source, target, path): random JSON documents (S: edge cases; M/L: 600 / 30000-node trees) with mutated copies. Driver calls json::diff on const references and hashes dump() of the patch.
Driver compiled with g++ -O2 -std=c++11 -fno-access-control -I/w/include, binary cached in /build/drv/<md5 of include/**/*.hpp + driver>; /w is never written.
Workloads are seeded by gen_workload.py (fixed seeds 20191111+i); inputs are within the contract of the function (see spec).
