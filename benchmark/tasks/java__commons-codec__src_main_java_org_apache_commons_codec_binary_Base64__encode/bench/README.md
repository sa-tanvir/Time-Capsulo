Same as the Base32 task but with Base64 (standard or URL-safe alphabet). Workload lines: lineLength urlSafe sepKind chunk length seed.
The driver is TCBench.java in the same package as the target; it compiles against target/classes (build output goes to /tmp/tcb). It reads /task/bench/workload_<size>.txt produced by gen_workload.py.
