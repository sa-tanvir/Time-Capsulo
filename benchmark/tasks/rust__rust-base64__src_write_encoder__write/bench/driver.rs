
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `EncoderWriter::write`. Env: TC_SIZE, TC_REPEAT, TC_MODE, TC_TASK.
    use super::*;
    use crate::CharacterSet;
    use std::io;
    use std::time::Instant;

    fn xs(x: &mut u64) -> u64 {
        *x ^= *x >> 12; *x ^= *x << 25; *x ^= *x >> 27;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }

    fn charset(s: &str) -> CharacterSet {
        match s { "S" => CharacterSet::Standard, "U" => CharacterSet::UrlSafe, _ => CharacterSet::Crypt }
    }

    /// Delegate that accepts at most `cap` bytes per call (0 = all) and fails every `intr`-th call.
    struct Throttle { v: Vec<u8>, cap: usize, intr: usize, calls: usize }
    impl Write for Throttle {
        fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
            self.calls += 1;
            if self.intr > 0 && self.calls % self.intr == 0 {
                return Err(io::Error::new(ErrorKind::Interrupted, "interrupted"));
            }
            let n = if self.cap == 0 { buf.len() } else { cmp::min(self.cap, buf.len()) };
            self.v.extend_from_slice(&buf[..n]);
            Ok(n)
        }
        fn flush(&mut self) -> io::Result<()> { Ok(()) }
    }

    struct Case { config: Config, data: Vec<u8>, sizes: Vec<usize>, sink: Throttle }

    fn load() -> Vec<Case> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let config = Config::new(charset(f[0]), f[1] == "1");
            let len: usize = f[2].parse().unwrap();
            let mut x: u64 = f[3].parse::<u64>().unwrap() | 1;
            let data: Vec<u8> = (0..len).map(|_| (xs(&mut x) >> 56) as u8).collect();
            let maxw: usize = f[4].parse().unwrap();
            let sizes: Vec<usize> = (0..97).map(|_| (xs(&mut x) % (maxw as u64 + 1)) as usize).collect();
            let sink = Throttle { v: Vec::with_capacity(len * 4 / 3 + 8), cap: f[5].parse().unwrap(),
                                  intr: f[6].parse().unwrap(), calls: 0 };
            Case { config, data, sizes, sink }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for b in s {
            *h ^= *b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    /// Feeds the whole input through `write` (retrying Interrupted), then finishes. Returns the write results.
    fn run(c: &mut Case, log: &mut Vec<u64>) {
        c.sink.v.clear();
        c.sink.calls = 0;
        let data = &c.data;
        let sizes = &c.sizes;
        let mut enc = EncoderWriter::new(&mut c.sink, c.config);
        let mut pos = 0;
        let mut k = 0;
        while pos < data.len() {
            let end = cmp::min(data.len(), pos + sizes[k % sizes.len()]);
            k += 1;
            match enc.write(&data[pos..end]) {
                Ok(n) => { pos += n; log.push(n as u64); }
                Err(_) => log.push(u64::max_value()),
            }
        }
        while enc.finish().is_err() {}
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let mut cases = load();
        let mut log: Vec<u64> = Vec::with_capacity(1 << 16);
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter_mut() {
                log.clear();
                run(c, &mut log);
                fnv(&mut h, format!("{:?}|{}|", log, c.sink.v.len()).as_bytes());
                fnv(&mut h, &c.sink.v);
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter_mut() {
                    log.clear();
                    run(c, &mut log);
                    acc = acc.wrapping_add(c.sink.v.len() as u64).wrapping_add(log.len() as u64);
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
