binary_reader::get_cbor_string: hex-encoded CBOR text strings (all length forms, indefinite chunks, errors). The driver builds a reader with a throwing recording SAX handler, reads the first byte, then times the call.
Driver compiled with g++ -O2 -std=c++11 -fno-access-control -I/w/include, binary cached in /build/drv/<md5 of include/**/*.hpp + driver>; /w is never written.
Workloads are seeded by gen_workload.py (fixed seeds 20191111+i); inputs are within the contract of the function (see spec).
