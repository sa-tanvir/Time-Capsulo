lexer::scan: hex input bytes; the driver calls scan() until end_of_input/parse_error and records token kinds, value sizes/bits and positions.
Driver compiled with g++ -O2 -std=c++11 -fno-access-control -I/w/include, binary cached in /build/drv/<md5 of include/**/*.hpp + driver>; /w is never written.
Workloads are seeded by gen_workload.py (fixed seeds 20191111+i); inputs are within the contract of the function (see spec).
