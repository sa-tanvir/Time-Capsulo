
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `read_varu32`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use std::time::Instant;

    struct Rng(u64);
    impl Rng {
        fn next(&mut self) -> u64 {
            self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
            let mut z = self.0;
            z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
            z ^ (z >> 31)
        }
        fn below(&mut self, n: u64) -> u64 { self.next() % n }
    }

    fn gen(seed: u64, count: usize, tail: bool) -> Vec<u8> {
        let mut r = Rng(seed);
        let mut v = Vec::with_capacity(count * 3 + 8);
        for _ in 0..count {
            let bits = [7u64, 7, 7, 14, 14, 21, 28, 32][r.below(8) as usize];
            let mut n = (r.next() & ((1u64 << bits) - 1)) as u32;
            let mut enc = Vec::with_capacity(5);
            while n >= 0x80 { enc.push((n as u8) | 0x80); n >>= 7; }
            enc.push(n as u8);
            if r.below(10) == 0 {               // redundant padding: ... 0x80 ... 0x00, still <= 5 bytes
                while enc.len() < 5 && r.below(2) == 0 { let l = enc.len(); enc[l - 1] |= 0x80; enc.push(0); }
            }
            v.extend(enc);
        }
        if tail { for _ in 0..1 + r.below(4) { v.push(0x80 | r.below(128) as u8); } }
        v
    }

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
    }

    fn load() -> Vec<(usize, bool, Vec<u8>)> {
        let task = ::std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = ::std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = ::std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let reps: usize = f[1].parse().unwrap();
            if f[0] == "L" { (reps, false, unhex(f.get(2).cloned().unwrap_or(""))) }
            else { (reps, true, gen(f[2].parse().unwrap(), f[3].parse().unwrap(), f[4] == "1")) }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for &b in s {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    fn bb<T>(x: T) -> T { unsafe { let r = ::std::ptr::read_volatile(&x); ::std::mem::forget(x); r } }

    fn decode_all<F: FnMut(u32, usize)>(buf: &[u8], stream: bool, mut f: F) {
        if !stream { let (n, k) = read_varu32(buf); f(n, k); return; }
        let mut pos = 0;
        loop {
            let (n, k) = read_varu32(&buf[pos..]);
            f(n, k);
            if k == 0 { break; }
            pos += k;
        }
    }

    #[test]
    fn tc_bench() {
        let mode = match ::std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = ::std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let cases = load();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let mut s = String::new();
                decode_all(&c.2, c.1, |n, k| s.push_str(&format!("{}:{},", n, k)));
                fnv(&mut h, s.as_bytes());
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    for _ in 0..c.0 {
                        let buf: &[u8] = bb(&c.2[..]);
                        decode_all(buf, c.1, |n, k| acc = acc.wrapping_add(n as u64 ^ k as u64));
                    }
                }
            }
            let el = t0.elapsed();
            let el = el.as_secs() as f64 + el.subsec_nanos() as f64 * 1e-9;
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
