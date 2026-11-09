Calls colognePhonetic on generated words (letters, umlauts, separators). Word length grows ~10x per size.
The driver is TCBench.java in the same package as the target; it compiles against target/classes (build output goes to /tmp/tcb). It reads /task/bench/workload_<size>.txt produced by gen_workload.py.
