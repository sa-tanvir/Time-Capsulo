
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `InstRanges::matches`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
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

    fn scalar(r: &mut Rng, hi: u32) -> u32 {
        loop {
            let c = r.below(hi as u64 + 1) as u32;
            if c < 0xD800 || c > 0xDFFF { return c; }
        }
    }

    fn ch(v: u32) -> Option<char> { ::std::char::from_u32(v) }

    fn gen(seed: u64, n: usize, region: &str, nq: usize) -> (Vec<(char, char)>, Vec<Char>) {
        let mut r = Rng(seed);
        let hi = match region { "ascii" => 0xFF, "bmp" => 0xFFFF, _ => 0x10FFFF };
        let mut pts: Vec<u32> = Vec::new();
        while pts.len() < 2 * n {
            pts.push(scalar(&mut r, hi));
            if pts.len() == 2 * n { pts.sort(); pts.dedup(); }
        }
        let ranges: Vec<(char, char)> = pts.chunks(2).map(|p| (ch(p[0]).unwrap(), ch(p[1]).unwrap())).collect();
        let mut qs = Vec::with_capacity(nq);
        while qs.len() < nq {
            let q: Option<char> = match r.below(8) {
                0 | 1 => { let p = pts[r.below(pts.len() as u64) as usize]; ch(p) }
                2 => { let p = pts[r.below(pts.len() as u64) as usize]; ch(p.wrapping_add(1)) }
                3 => { let p = pts[r.below(pts.len() as u64) as usize]; ch(p.wrapping_sub(1)) }
                4 => ch(r.below(0x80) as u32),
                5 => None,
                _ => ch(scalar(&mut r, hi)),
            };
            if q.is_none() && r.below(4) != 0 { continue; }
            qs.push(Char::from(q));
        }
        (ranges, qs)
    }

    fn hexc(s: &str) -> Char {
        if s == "none" { Char::from(None) } else { Char::from(ch(u32::from_str_radix(s, 16).unwrap()).unwrap()) }
    }

    fn load() -> Vec<(usize, InstRanges, Vec<Char>)> {
        let task = ::std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = ::std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = ::std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let reps: usize = f[1].parse().unwrap();
            let (ranges, qs) = if f[0] == "L" {
                let rs = f[2].split(',').map(|p| {
                    let ab: Vec<&str> = p.split('-').collect();
                    (ch(u32::from_str_radix(ab[0], 16).unwrap()).unwrap(), ch(u32::from_str_radix(ab[1], 16).unwrap()).unwrap())
                }).collect();
                (rs, f[3].split(',').map(hexc).collect())
            } else {
                gen(f[2].parse().unwrap(), f[3].parse().unwrap(), f[4], f[5].parse().unwrap())
            };
            (reps, InstRanges { goto: 0, ranges: ranges }, qs)
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for &b in s {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    fn bb<T>(x: T) -> T { unsafe { let r = ::std::ptr::read_volatile(&x); ::std::mem::forget(x); r } }

    #[test]
    fn tc_bench() {
        let mode = match ::std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = ::std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let cases = load();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let s: Vec<u8> = c.2.iter().map(|&q| if c.1.matches(q) { b'1' } else { b'0' }).collect();
                fnv(&mut h, format!("{}:", c.1.ranges.len()).as_bytes());
                fnv(&mut h, &s);
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    let inst: &InstRanges = bb(&c.1);
                    for _ in 0..c.0 {
                        for &q in c.2.iter() {
                            acc = acc.wrapping_add(inst.matches(bb(q)) as u64);
                        }
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
