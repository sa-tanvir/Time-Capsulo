
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `ChunkedEncoder::encode`. Env: TC_SIZE, TC_REPEAT, TC_MODE, TC_TASK.
    use super::*;
    use crate::CharacterSet;
    use std::time::Instant;

    fn rand_bytes(n: usize, seed: u64) -> Vec<u8> {
        let mut x = seed | 1;
        (0..n).map(|_| {
            x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
            (x.wrapping_mul(0x2545_F491_4F6C_DD1D) >> 56) as u8
        }).collect()
    }

    fn charset(s: &str) -> CharacterSet {
        match s { "S" => CharacterSet::Standard, "U" => CharacterSet::UrlSafe, _ => CharacterSet::Crypt }
    }

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
    }

    struct VecSink<'a> { v: &'a mut Vec<u8> }
    impl<'a> Sink for VecSink<'a> {
        type Error = ();
        fn write_encoded_bytes(&mut self, encoded: &[u8]) -> Result<(), ()> {
            self.v.extend_from_slice(encoded);
            Ok(())
        }
    }

    struct Case { data: Vec<u8>, enc: ChunkedEncoder, out: Vec<u8> }

    fn load() -> Vec<Case> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let config = Config::new(charset(f[1]), f[2] == "1");
            let data = if f[0] == "lit" {
                unhex(f.get(3).cloned().unwrap_or(""))
            } else {
                rand_bytes(f[3].parse().unwrap(), f[4].parse().unwrap())
            };
            let out = Vec::with_capacity(data.len() * 4 / 3 + 8);
            Case { data, enc: ChunkedEncoder::new(config), out }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for b in s {
            *h ^= *b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let mut cases = load();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter_mut() {
                c.out.clear();
                let r = c.enc.encode(&c.data, &mut VecSink { v: &mut c.out });
                fnv(&mut h, format!("{:?} {} ", r, c.out.len()).as_bytes());
                fnv(&mut h, &c.out);
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter_mut() {
                    c.out.clear();
                    let _ = c.enc.encode(&c.data, &mut VecSink { v: &mut c.out });
                    acc = acc.wrapping_add(c.out.len() as u64).wrapping_add(*c.out.last().unwrap_or(&0) as u64);
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
