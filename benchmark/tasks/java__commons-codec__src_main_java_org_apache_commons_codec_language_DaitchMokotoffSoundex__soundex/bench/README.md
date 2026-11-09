The target is private; the driver calls the public soundex(String) (branching mode) and encode(String) (non-branching mode), which delegate to it, with and without folding.
The driver is TCBench.java in the same package as the target; it compiles against target/classes (build output goes to /tmp/tcb). It reads /task/bench/workload_<size>.txt produced by gen_workload.py.
