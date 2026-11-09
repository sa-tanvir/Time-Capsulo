
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `FreqyPacked::find`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
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

    const TEXT: &'static [u8] = b"eeeeeeeeeeeettttttttaaaaaaaaoooooooiiiiiiinnnnnnnsssssshhhhhhrrrrrrddddllllcccuuummwwffggyyppbbvkjxqz          ,.";

    fn byte(r: &mut Rng, alpha: &str) -> u8 {
        match alpha {
            "text" => TEXT[r.below(TEXT.len() as u64) as usize],
            "dna" => b"ACGT"[r.below(4) as usize],
            "bin2" => r.below(2) as u8,
            "bin256" => r.below(256) as u8,
            _ => if r.below(50) == 0 { r.below(256) as u8 } else { 0 },
        }
    }

    fn gen(seed: u64, hay_len: usize, alpha: &str, pat_len: usize, plant: i64, near: usize) -> (Vec<u8>, Vec<u8>) {
        let mut r = Rng(seed);
        let pat: Vec<u8> = (0..pat_len).map(|_| byte(&mut r, alpha)).collect();
        let mut hay: Vec<u8> = (0..hay_len).map(|_| byte(&mut r, alpha)).collect();
        if hay_len > pat_len {
            for _ in 0..near {
                let at = r.below((hay_len - pat_len) as u64) as usize;
                hay[at..at + pat_len].copy_from_slice(&pat);
                let k = r.below(pat_len as u64) as usize;
                hay[at + k] = hay[at + k].wrapping_add(1 + r.below(255) as u8);
            }
            if plant >= 0 {
                let at = (hay_len - pat_len) * plant as usize / 1000;
                hay[at..at + pat_len].copy_from_slice(&pat);
            }
        }
        (pat, hay)
    }

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
    }

    fn load() -> Vec<(usize, Vec<u8>, Vec<u8>)> {
        let task = ::std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = ::std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = ::std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let reps: usize = f[1].parse().unwrap();
            if f[0] == "L" {
                (reps, unhex(f.get(2).cloned().unwrap_or("")), unhex(f.get(3).cloned().unwrap_or("")))
            } else {
                let (p, h) = gen(f[2].parse().unwrap(), f[3].parse().unwrap(), f[4], f[5].parse().unwrap(),
                                 f[6].parse().unwrap(), f[7].parse().unwrap());
                (reps, p, h)
            }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &str) {
        for b in s.bytes() {
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
        let searchers: Vec<FreqyPacked> = cases.iter().map(|c| FreqyPacked::new(c.1.clone())).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for (c, s) in cases.iter().zip(searchers.iter()) {
                fnv(&mut h, &format!("{}:{:?}\n", c.1.len(), s.find(&c.2)));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for (c, s) in cases.iter().zip(searchers.iter()) {
                    for _ in 0..c.0 {
                        let hay: &[u8] = bb(&c.2[..]);
                        acc = acc.wrapping_add(s.find(hay).map(|x| x as u64 + 1).unwrap_or(0));
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
