
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `<OptBuilder as Display>::fmt`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use std::time::Instant;

    fn read_lines() -> Vec<String> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| l.to_string()).collect()
    }

    fn fnv(h: &mut u64, s: &str) {
        for b in s.bytes() {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    fn bb<T>(x: T) -> T { let y = unsafe { std::ptr::read_volatile(&x) }; std::mem::forget(x); y }

    const WORDS: [&str; 24] = ["file", "name", "val", "path", "out", "in", "x", "level", "mode", "key", "port", "host",
        "user", "FILE", "PATH", "N", "count", "dir", "spec", "pattern", "\u{e4}rger", "\u{6570}", "id", "url"];

    fn opt(s: &'static str) -> Option<&'static str> { if s == "-" { None } else { Some(s) } }

    fn build(line: &'static str) -> OptBuilder<'static, 'static> {
        let f: Vec<&'static str> = line.split('\t').collect();
        let mut o = OptBuilder::new(f[0]);
        o.s.long = opt(f[1]);
        o.s.short = opt(f[2]).map(|s| s.chars().next().unwrap());
        if f[3].contains('M') { o.b.settings.set(ArgSettings::Multiple); }
        if f[3].contains('E') { o.b.settings.set(ArgSettings::RequireEquals); }
        if f[3].contains('D') { o.b.settings.set(ArgSettings::RequireDelimiter); }
        o.b.settings.set(ArgSettings::TakesValue);
        o.v.val_delim = opt(f[4]).map(|s| s.chars().next().unwrap());
        o.v.num_vals = opt(f[5]).map(|s| s.parse().unwrap());
        if let Some(names) = opt(f[6]) {
            let mut vm = VecMap::new();
            if names.starts_with('#') {
                let mut it = names[1..].split(':');
                let count: usize = it.next().unwrap().parse().unwrap();
                let seed: usize = it.next().unwrap().parse().unwrap();
                for i in 0..count { vm.insert(i, WORDS[(seed + 7 * i) % WORDS.len()]); }
            } else {
                for (i, n) in names.split(' ').enumerate() { vm.insert(i, n); }
            }
            o.v.val_names = Some(vm);
        }
        o
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let lines: &'static Vec<String> = Box::leak(Box::new(read_lines()));
        let inputs: Vec<OptBuilder<'static, 'static>> = lines.iter().map(|l| build(l.as_str())).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for o in inputs.iter() {
                fnv(&mut h, &format!("{}\n", o));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", inputs.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for o in inputs.iter() {
                    let s = format!("{}", bb(o));
                    acc = acc.wrapping_add(s.len() as u64);
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", inputs.len(), repeat, el);
        }
    }
}
