
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `decode_last_utf8`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
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

    fn push_char(r: &mut Rng, v: &mut Vec<u8>) {
        let cp = match r.below(4) {
            0 => r.below(0x80) as u32,
            1 => 0x80 + r.below(0x800 - 0x80) as u32,
            2 => { let c = 0x800 + r.below(0x10000 - 0x800) as u32; if c >= 0xD800 && c < 0xE000 { c - 0x1000 } else { c } }
            _ => 0x10000 + r.below(0x110000 - 0x10000) as u32,
        };
        let c = ::std::char::from_u32(cp).unwrap();
        let mut buf = [0u8; 4];
        v.extend_from_slice(c.encode_utf8(&mut buf).as_bytes());
    }

    fn push_bad(r: &mut Rng, v: &mut Vec<u8>) {
        match r.below(7) {
            0 => v.push(0x80 + r.below(0x40) as u8),                         // stray continuation
            1 => { let mut t = Vec::new(); while t.len() < 2 { t.clear(); push_char(r, &mut t); } t.pop(); v.extend(t); } // truncated
            2 => { v.push(0xC0 + r.below(2) as u8); v.push(0x80 + r.below(0x40) as u8); }        // overlong 2
            3 => { v.push(0xE0); v.push(0x80 + r.below(0x20) as u8); v.push(0x80 + r.below(0x40) as u8); } // overlong 3
            4 => { v.push(0xED); v.push(0xA0 + r.below(0x20) as u8); v.push(0x80 + r.below(0x40) as u8); } // surrogate
            5 => v.push(0xF8 + r.below(8) as u8),                           // never valid
            _ => { v.push(0xF4 + r.below(4) as u8); v.push(0x90 + r.below(0x30) as u8); v.push(0x80); v.push(0x80); } // > U+10FFFF
        }
    }

    fn gen(seed: u64, len: usize, bad: u64) -> Vec<u8> {
        let mut r = Rng(seed);
        let mut v = Vec::with_capacity(len + 8);
        while v.len() < len {
            if r.below(1000) < bad { push_bad(&mut r, &mut v) } else { push_char(&mut r, &mut v) }
        }
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
            else { (reps, true, gen(f[2].parse().unwrap(), f[3].parse().unwrap(), f[4].parse().unwrap())) }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for &b in s {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    fn bb<T>(x: T) -> T { unsafe { let r = ::std::ptr::read_volatile(&x); ::std::mem::forget(x); r } }

    /// Backward walk: decode the last char of buf[..i]; on failure step back one byte.
    fn walk<F: FnMut(Option<(char, usize)>)>(buf: &[u8], walk_all: bool, mut f: F) {
        if !walk_all { f(decode_last_utf8(buf)); return; }
        let mut i = buf.len();
        while i > 0 {
            let r = decode_last_utf8(&buf[..i]);
            i -= match r { Some((_, n)) => n, None => 1 };
            f(r);
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
                walk(&c.2, c.1, |r| match r {
                    None => s.push_str("N,"),
                    Some((ch, n)) => s.push_str(&format!("{}:{},", ch as u32, n)),
                });
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
                        walk(buf, c.1, |r| acc = acc.wrapping_add(match r { None => 7, Some((ch, n)) => ch as u64 + n as u64 }));
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
