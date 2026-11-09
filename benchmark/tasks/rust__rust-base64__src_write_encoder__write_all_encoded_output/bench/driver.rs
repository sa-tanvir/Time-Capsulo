
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `EncoderWriter::write_all_encoded_output`. Env: TC_SIZE, TC_REPEAT, TC_MODE, TC_TASK.
    use super::*;
    use crate::STANDARD;
    use std::io;
    use std::time::{Duration, Instant};

    fn xs(x: &mut u64) -> u64 {
        *x ^= *x >> 12; *x ^= *x << 25; *x ^= *x >> 27;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }

    /// Delegate: accepts at most `cap` bytes (0 = all; every 10th call accepts 0 when cap > 0),
    /// Interrupted on every `intr`-th call, ErrorKind::Other on call `fail_at`.
    struct Throttle { v: Vec<u8>, cap: usize, intr: usize, fail_at: usize, calls: usize }
    impl Write for Throttle {
        fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
            self.calls += 1;
            if self.fail_at == self.calls {
                return Err(io::Error::new(ErrorKind::Other, "boom"));
            }
            if self.intr > 0 && self.calls % self.intr == 0 {
                return Err(io::Error::new(ErrorKind::Interrupted, "interrupted"));
            }
            let n = if self.cap == 0 { buf.len() } else if self.calls % 10 == 7 { 0 } else { cmp::min(self.cap, buf.len()) };
            self.v.extend_from_slice(&buf[..n]);
            Ok(n)
        }
        fn flush(&mut self) -> io::Result<()> { Ok(()) }
    }

    struct Case { pending: Vec<u8>, sink: Throttle }

    fn load() -> Vec<Case> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        let table = STANDARD.char_set.encode_table();
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<usize> = l.split('\t').map(|s| s.parse().unwrap()).collect();
            let mut x = (f[1] as u64) | 1;
            let pending: Vec<u8> = (0..f[0]).map(|_| table[(xs(&mut x) >> 58) as usize]).collect();
            Case { pending, sink: Throttle { v: Vec::with_capacity(BUF_SIZE), cap: f[2], intr: f[3], fail_at: f[4], calls: 0 } }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for b in s {
            *h ^= *b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    /// Builds the writer state outside the timed region, times only the call.
    fn run(c: &mut Case, el: &mut Duration) -> (String, usize) {
        c.sink.v.clear();
        c.sink.calls = 0;
        let pending = &c.pending;
        let mut enc = EncoderWriter::new(&mut c.sink, STANDARD);
        enc.output[..pending.len()].copy_from_slice(pending);
        enc.output_occupied_len = pending.len();
        let t0 = Instant::now();
        let r = enc.write_all_encoded_output();
        *el += t0.elapsed();
        let left = enc.output_occupied_len;
        let rs = match r { Ok(()) => "ok".to_string(), Err(e) => format!("{:?}", e.kind()) };
        enc.output_occupied_len = 0; // keep Drop/finish from touching the delegate again
        enc.finished = true;
        (rs, left)
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let mut cases = load();
        let mut el = Duration::new(0, 0);
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter_mut() {
                let (r, left) = run(c, &mut el);
                fnv(&mut h, format!("{}|{}|{}|", r, left, c.sink.calls).as_bytes());
                fnv(&mut h, &c.sink.v);
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            for _ in 0..repeat {
                for c in cases.iter_mut() {
                    let (_, left) = run(c, &mut el);
                    acc = acc.wrapping_add(c.sink.v.len() as u64).wrapping_add(left as u64);
                }
            }
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el.as_secs_f64());
        }
    }
}
