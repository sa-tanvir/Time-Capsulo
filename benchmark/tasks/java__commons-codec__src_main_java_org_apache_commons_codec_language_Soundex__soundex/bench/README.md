Calls soundex on generated words with the three predefined Soundex instances (US_ENGLISH, US_ENGLISH_SIMPLIFIED, US_ENGLISH_GENEALOGY).
The driver is TCBench.java in the same package as the target; it compiles against target/classes (build output goes to /tmp/tcb). It reads /task/bench/workload_<size>.txt produced by gen_workload.py.
