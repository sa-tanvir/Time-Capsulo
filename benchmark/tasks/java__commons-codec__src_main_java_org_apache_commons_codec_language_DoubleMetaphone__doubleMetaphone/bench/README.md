Calls doubleMetaphone(word, false) and (word, true) on generated words from name-like fragments; the code length limit is set in the first workload line so output length grows with input length.
The driver is TCBench.java in the same package as the target; it compiles against target/classes (build output goes to /tmp/tcb). It reads /task/bench/workload_<size>.txt produced by gen_workload.py.
