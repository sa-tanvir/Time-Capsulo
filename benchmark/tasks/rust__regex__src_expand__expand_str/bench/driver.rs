
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `expand_str`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use std::time::Instant;
    use ::re_unicode::{Regex, Captures};

    const PATTERNS: [&'static str; 8] = [
        r"(?P<a>\w+)\s+(?P<b>\d+)", r"(?P<foo>\w+)", r"(?P<first>\S+)\s+(?P<last>\S+)(?P<space>\s*)",
        r"(\w) (\w)?", r"(.)(.)", r"(?P<x_1>[a-z]+)(?P<Y2>[0-9]+)?(?P<_z>!)?", r"(\S+)\s+(\S+)", r"(.)",
    ];
    const TEXTS: [&'static str; 8] = ["abc 123", "abc", "w1 w2 w3 w4", "a ", "ab", "hello42", "w1 w2", "b"];

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

    const LIT: [&'static str; 10] = [" ", "-", ".", "z", "foo bar", "_", "\u{e9}t\u{e9}", "\u{65e5}\u{672c}", ", ", "}"];

    fn gen_template(seed: u64, len: usize, names: &[String], ngroups: usize) -> Vec<u8> {
        let mut r = Rng(seed);
        let mut t: Vec<u8> = Vec::with_capacity(len + 32);
        while t.len() < len {
            let piece: String = match r.below(12) {
                0 | 1 => LIT[r.below(10) as usize].to_string(),
                2 => format!("${}", r.below(ngroups as u64 + 2)),
                3 => format!("${{{}}}", r.below(ngroups as u64 + 2)),
                4 | 5 => if names.is_empty() { "$9".to_string() } else { format!("${}", names[r.below(names.len() as u64) as usize]) },
                6 => if names.is_empty() { "${9}".to_string() } else { format!("${{{}}}", names[r.below(names.len() as u64) as usize]) },
                7 => "$$".to_string(),
                8 => ["$ ", "$-", "${", "${}", "$\u{e9}", "${a b}"][r.below(6) as usize].to_string(),
                9 => ["$99999999999", "$007", "${4294967296}", "$nope", "${nope}"][r.below(5) as usize].to_string(),
                10 => "\u{2603}$1\u{2603}".to_string(),
                _ => format!("[{}]", r.below(1000)),
            };
            t.extend_from_slice(piece.as_bytes());
        }
        if r.below(4) == 0 { t.push(b'$'); }
        t
    }

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
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
        let task = ::std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = ::std::env::var("TC_SIZE").expect("TC_SIZE");
        let wl = ::std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        let res: Vec<Regex> = PATTERNS.iter().map(|p| Regex::new(p).unwrap()).collect();
        let texts: Vec<String> = TEXTS.iter().map(|t| t.to_string()).collect();
        let caps: Vec<Captures> = res.iter().zip(texts.iter()).map(|(re, t)| re.captures(t).unwrap()).collect();
        // case = (reps, pattern index, template)
        let cases: Vec<(usize, usize, String)> = wl.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let (reps, pat): (usize, usize) = (f[1].parse().unwrap(), f[2].parse().unwrap());
            let raw = if f[0] == "L" { unhex(f.get(3).cloned().unwrap_or("")) } else {
                let names: Vec<String> = res[pat].capture_names().filter_map(|n| n.map(|s| s.to_string())).collect();
                gen_template(f[3].parse().unwrap(), f[4].parse().unwrap(), &names, res[pat].captures_len())
            };
            (reps, pat, String::from_utf8(raw).unwrap())
        }).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let mut dst = String::from("PRE:");
                expand_str(&caps[c.1], &c.2[..], &mut dst);
                fnv(&mut h, dst.as_bytes());
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let mut dst = String::from("PRE:");
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    for _ in 0..c.0 {
                        dst.clear();
                        expand_str(&caps[c.1], bb(&c.2[..]), &mut dst);
                        acc = acc.wrapping_add(dst.len() as u64);
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
