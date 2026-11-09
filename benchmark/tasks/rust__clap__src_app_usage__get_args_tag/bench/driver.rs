
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `usage::get_args_tag`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use args::{Arg, ArgGroup};
    use app::App;
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
    fn leak(s: String) -> &'static str { Box::leak(s.into_boxed_str()) }

    struct R(u64);
    impl R {
        fn next(&mut self) -> u64 { self.0 ^= self.0 << 13; self.0 ^= self.0 >> 7; self.0 ^= self.0 << 17; self.0 }
        fn below(&mut self, n: u64) -> u64 { self.next() % n }
    }

    // (name, flags, value names)
    type Spec = Vec<(&'static str, String, Vec<&'static str>)>;

    fn build_app(dont_collapse: bool, spec: Spec) -> App<'static, 'static> {
        let mut app = App::new("prog");
        if dont_collapse { app = app.setting(AS::DontCollapseArgsInUsage); }
        let mut req_g: Vec<&'static str> = Vec::new();
        let mut opt_g: Vec<&'static str> = Vec::new();
        for (i, (name, fl, vn)) in spec.into_iter().enumerate() {
            let mut a = Arg::with_name(name).index(i as u64 + 1);
            if fl.contains('R') { a = a.required(true); }
            if fl.contains('H') { a = a.hidden(true); }
            if fl.contains('L') { a = a.last(true); }
            if fl.contains('M') { a = a.multiple(true); }
            if !vn.is_empty() { a = a.value_names(Box::leak(vn.into_boxed_slice())); }
            if fl.contains('G') { req_g.push(name); }
            if fl.contains('g') { opt_g.push(name); }
            app = app.arg(a);
        }
        let rg = Box::leak(req_g.into_boxed_slice());
        let og = Box::leak(opt_g.into_boxed_slice());
        if !rg.is_empty() { app = app.group(ArgGroup::with_name("reqgrp").args(rg).required(true)); }
        if !og.is_empty() { app = app.group(ArgGroup::with_name("optgrp").args(og)); }
        app.group(ArgGroup::with_name("unrelated").args(&["zz1", "zz2"]))
    }

    fn build(line: &str) -> App<'static, 'static> {
        let f: Vec<&str> = line.split('\t').collect();
        let dc = f[1] == "1";
        let mut spec: Spec = Vec::new();
        if f[0] == "L" {
            for item in f[2].split(' ').filter(|s| !s.is_empty()) {
                let p: Vec<&str> = item.split(':').collect();
                let vn: Vec<&'static str> = p.get(2).map(|v| v.split(',').map(|x| leak(x.to_string())).collect()).unwrap_or_default();
                spec.push((leak(p[0].to_string()), p.get(1).cloned().unwrap_or("").to_string(), vn));
            }
        } else {
            let n: u64 = f[2].parse().unwrap();
            let pct: u64 = f[3].parse().unwrap();
            let mut r = R(f[4].parse::<u64>().unwrap().wrapping_mul(0x9E37_79B9_7F4A_7C15) | 1);
            for i in 0..n {
                let mut fl = String::new();
                for c in ['R', 'H', 'L', 'M', 'G', 'g'].iter() {
                    let p = if *c == 'L' || *c == 'G' || *c == 'g' { pct / 3 } else { pct };
                    if r.below(100) < p { fl.push(*c); }
                }
                if fl.contains('G') && fl.contains('g') { fl = fl.replace("g", ""); }
                let vn: Vec<&'static str> = if r.below(4) == 0 {
                    (0..1 + r.below(3)).map(|j| leak(format!("V{}x{}", i, j))).collect()
                } else { Vec::new() };
                spec.push((leak(format!("p{}", i)), fl, vn));
            }
        }
        build_app(dc, spec)
    }

    fn show(o: &Option<String>) -> String { match *o { None => "None".to_string(), Some(ref s) => format!("Some({})", s) } }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let apps: Vec<App<'static, 'static>> = read_lines().iter().map(|l| build(l)).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for a in apps.iter() {
                fnv(&mut h, &format!("{}|{}\n", show(&get_args_tag(&a.p, true)), show(&get_args_tag(&a.p, false))));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", apps.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for a in apps.iter() {
                    for &ir in [true, false].iter() {
                        acc = acc.wrapping_add(get_args_tag(&bb(a).p, bb(ir)).map_or(1, |s| s.len() as u64));
                    }
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", apps.len(), repeat, el);
        }
    }
}
