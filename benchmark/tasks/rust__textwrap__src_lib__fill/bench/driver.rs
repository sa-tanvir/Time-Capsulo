
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Wrapper::fill`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use std::time::Instant;

    fn unesc(s: &str) -> String {
        let mut out = String::with_capacity(s.len());
        let mut it = s.chars();
        while let Some(c) = it.next() {
            if c == '\\' {
                match it.next() {
                    Some('n') => out.push('\n'),
                    Some('t') => out.push('\t'),
                    Some('r') => out.push('\r'),
                    Some(o) => out.push(o),
                    None => {}
                }
            } else {
                out.push(c);
            }
        }
        out
    }

    struct Case { reps: usize, width: usize, brk: bool, ii: String, si: String, s: String }

    fn load() -> Vec<Case> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.split('\n').filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.splitn(6, '\t').collect();
            let width = if f[1] == "max" { usize::max_value() } else { f[1].parse().unwrap() };
            Case { reps: f[0].parse().unwrap(), width: width, brk: f[2] == "1",
                   ii: unesc(f[3]), si: unesc(f[4]), s: unesc(f[5]) }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &str) {
        for b in s.bytes() {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    fn bb<T: Copy>(x: T) -> T { unsafe { std::ptr::read_volatile(&x) } }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let cases = load();
        let wrappers: Vec<Wrapper<HyphenSplitter>> = cases.iter().map(|c| {
            Wrapper::new(c.width).initial_indent(&c.ii).subsequent_indent(&c.si).break_words(c.brk)
        }).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for (c, w) in cases.iter().zip(wrappers.iter()) {
                let out = w.fill(&c.s);
                fnv(&mut h, &format!("{}|{}|{:?}\n", c.reps, out.len(), out));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for (c, w) in cases.iter().zip(wrappers.iter()) {
                    for _ in 0..c.reps {
                        let out = w.fill(bb(c.s.as_str()));
                        acc = acc.wrapping_add(out.len() as u64);
                    }
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
