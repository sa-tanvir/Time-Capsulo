
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `generic_hamming`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use std::time::Instant;

    const ALPHABET: &str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\u{f6}\u{fc}\u{9999}\u{999}\u{e9}\u{df}\u{436}\u{3bb}\u{20ac}\u{2713}\u{65e5}\u{672c}";

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

    /// Deterministic pair: `a` is random over the first `alpha` alphabet chars, `b` is `a` with
    /// `pct` percent of positions edited (mode "eq": substitutions/adjacent swaps only; "any": also indels).
    fn gen_pair(seed: u64, len: usize, alpha: usize, pct: u64, mode: &str) -> (String, String) {
        let al: Vec<char> = ALPHABET.chars().take(alpha).collect();
        let n = al.len() as u64;
        let mut r = Rng(seed);
        let a: Vec<char> = (0..len).map(|_| al[r.below(n) as usize]).collect();
        let mut b: Vec<char> = Vec::with_capacity(len + len / 4 + 1);
        let mut i = 0;
        while i < a.len() {
            if r.below(100) < pct {
                let op = if mode == "eq" { r.below(2) } else { r.below(4) };
                match op {
                    0 => { b.push(al[r.below(n) as usize]); i += 1; }
                    1 => if i + 1 < a.len() { b.push(a[i + 1]); b.push(a[i]); i += 2; } else { b.push(a[i]); i += 1; },
                    2 => { i += 1; }
                    _ => { b.push(al[r.below(n) as usize]); }
                }
            } else {
                b.push(a[i]);
                i += 1;
            }
        }
        (a.into_iter().collect(), b.into_iter().collect())
    }

    struct Case { reps: usize, a: String, b: String }

    fn load() -> Vec<Case> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let reps: usize = f[1].parse().unwrap();
            if f[0] == "L" {
                Case { reps, a: f[2].to_string(), b: f[3].to_string() }
            } else {
                let (a, b) = gen_pair(f[2].parse().unwrap(), f[3].parse().unwrap(), f[4].parse().unwrap(),
                                      f[5].parse().unwrap(), f[6]);
                Case { reps, a, b }
            }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &str) {
        for b in s.bytes() {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    /// Opaque identity so the optimiser cannot hoist repeated pure calls.
    fn bb<T: Copy>(x: T) -> T { unsafe { std::ptr::read_volatile(&x) } }

    type Input = (String, String);
    fn prep(c: &Case) -> Input { (c.a.clone(), c.b.clone()) }
    fn render(x: &Input) -> String { format!("{:?}", generic_hamming(x.0.chars(), x.1.chars())) }
    fn call(x: &Input) -> u64 {
        match generic_hamming(x.0.chars(), x.1.chars()) { Ok(n) => n as u64, Err(_) => 7 }
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let cases = load();
        let inputs: Vec<Input> = cases.iter().map(prep).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for (c, x) in cases.iter().zip(inputs.iter()) {
                let s = render(x);
                fnv(&mut h, &format!("{}|{}\n", c.reps, s));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for (c, x) in cases.iter().zip(inputs.iter()) {
                    for _ in 0..c.reps {
                        acc = acc.wrapping_add(call(bb(x)));
                    }
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
