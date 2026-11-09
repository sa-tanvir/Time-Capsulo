
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Regex::replacen` (re_bytes). Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use std::time::Instant;

    const PATTERNS: [&'static str; 17] = [
        r"\d", r"(?P<first>\S+)\s+(?P<last>\S+)(?P<space>\s*)", r"[aeiou]", r"x*", r"^[ \t]+|[ \t]+$", r"^",
        r"(\w) (\w)", r"foo", r"", r"\b", r"\d+", r"(\S+)\s+(\S+)", r"(.)(.)", r"(\w+) (\w+)", r"(.)", r"qzq",
        r"(?-u:\xFF)",
    ];
    const PLAIN: [&'static str; 4] = ["Z", "", "foo", "-"];
    const TEMPL: [&'static str; 10] = ["$2 $1", "$2 $$1", "$last $first$space", "$1-$2", "$2 $1", "$$1",
                                       "$2 $$c $1", "${1}a $1a", "[$0]", "<$1|${0}>$"];
    const NOEXP: [&'static str; 3] = ["$2 $1", "$$1", "${x}"];

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

    const WORDS: [&'static str; 16] = ["the", "quick", "fox", "foo", "bar", "xx", "aeiou", "rhythm", "w1", "42",
                                       "2018", "a", "boxx", "qzq", "under_score", "Zebra"];
    const SEPS: [&'static str; 6] = [" ", " ", " ", "  ", "\t", "\n"];

    fn gen_text(seed: u64, len: usize) -> Vec<u8> {
        let mut r = Rng(seed);
        let mut t: Vec<u8> = Vec::with_capacity(len + 16);
        while t.len() < len {
            match r.below(20) {
                0 => t.extend_from_slice(b"\xff\xfe"),
                1 => t.extend_from_slice("\u{65e5}\u{672c}\u{e9}".as_bytes()),
                _ => t.extend_from_slice(WORDS[r.below(16) as usize].as_bytes()),
            }
            t.extend_from_slice(SEPS[r.below(6) as usize].as_bytes());
        }
        t
    }

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
    }

    struct Case { reps: usize, pat: usize, kind: char, rep: usize, limit: usize, text: Vec<u8> }

    fn load() -> Vec<Case> {
        let task = ::std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = ::std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = ::std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let raw = if f[0] == "L" { unhex(f.get(6).cloned().unwrap_or("")) }
                      else { gen_text(f[6].parse().unwrap(), f[7].parse().unwrap()) };
            Case { reps: f[1].parse().unwrap(), pat: f[2].parse().unwrap(), kind: f[3].chars().next().unwrap(),
                   rep: f[4].parse().unwrap(), limit: f[5].parse().unwrap(), text: raw }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for &b in s {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    /// Runs one replacen call; returns (borrowed?, output, number of closure calls).
    fn run(re: &Regex, c: &Case, text: &[u8]) -> (bool, Vec<u8>, usize) {
        let mut calls = 0usize;
        let (borrowed, out) = {
            let out = match c.kind {
                'P' => re.replacen(text, c.limit, str::as_bytes(PLAIN[c.rep])),
                'T' => re.replacen(text, c.limit, str::as_bytes(TEMPL[c.rep])),
                'N' => re.replacen(text, c.limit, NoExpand(str::as_bytes(NOEXP[c.rep]))),
                _ => if c.rep == 0 {
                    re.replacen(text, c.limit, |caps: &Captures| { calls += 1; format!("<{}>", caps[0].len()).into_bytes() })
                } else {
                    re.replacen(text, c.limit, |caps: &Captures| { calls += 1; format!("{}:{}", caps.len(), caps.get(0).unwrap().start()).into_bytes() })
                },
            };
            let borrowed = match out { ::std::borrow::Cow::Borrowed(_) => true, _ => false };
            (borrowed, out.into_owned())
        };
        (borrowed, out, calls)
    }

    fn bb<T>(x: T) -> T { unsafe { let r = ::std::ptr::read_volatile(&x); ::std::mem::forget(x); r } }

    #[test]
    fn tc_bench() {
        let mode = match ::std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = ::std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let cases = load();
        let res: Vec<Regex> = PATTERNS.iter().map(|p| Regex::new(p).unwrap()).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let (b, out, calls) = run(&res[c.pat], c, &c.text);
                fnv(&mut h, format!("{}|{}|{}|", b, calls, out.len()).as_bytes());
                fnv(&mut h, &out[..]);
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    for _ in 0..c.reps {
                        let t: &[u8] = bb(&c.text[..]);
                        let (b, out, calls) = run(&res[c.pat], c, t);
                        acc = acc.wrapping_add(out.len() as u64 + calls as u64 + b as u64);
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
