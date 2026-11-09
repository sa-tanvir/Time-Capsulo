
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Validator::validate_arg_values`. Env: TC_SIZE, TC_REPEAT, TC_MODE, TC_TASK.
    use super::*;
    use args::{Arg, OptBuilder};
    use app::App;
    use std::ffi::{OsStr, OsString};
    use std::os::unix::ffi::OsStringExt;
    use std::time::Instant;

    const WORDS: [&str; 8] = ["alpha", "beta", "gamma", "x", "caf\u{e9}", "value-with-dashes", "42", "Zeta"];

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

    fn val(s: &str) -> OsString { if s == "~" { OsString::from_vec(vec![b'a', 0xff, b'b']) } else { OsString::from(s) } }

    struct Case { app: App<'static, 'static>, arg: OptBuilder<'static, 'static>, ma: MatchedArg, matcher: ArgMatcher<'static> }

    fn build(line: &str) -> Case {
        let f: Vec<&str> = line.splitn(3, '\t').collect();
        let fl = f[0];
        let mut a = Arg::with_name("opt").long("opt").short("o").takes_value(true).multiple(true);
        let pvs: Option<Vec<&'static str>> = if f[1] == "-" { None } else { Some(f[1].split(' ').map(|x| leak(x.to_string())).collect()) };
        if let Some(ref p) = pvs { a = a.possible_values(Box::leak(p.clone().into_boxed_slice())); }
        if fl.contains('C') { a = a.case_insensitive(true); }
        if fl.contains('E') { a = a.empty_values(true); } else { a = a.empty_values(false); }
        if fl.contains('V') { a = a.validator(|v: String| if v.contains("bad") { Err(format!("'{}' is bad", v)) } else { Ok(()) }); }
        if fl.contains('O') { a = a.validator_os(|v: &OsStr| if v.len() > 40 { Err(OsString::from("value too long")) } else { Ok(()) }); }
        let mut app = App::new("prog").arg(a).arg(Arg::with_name("other").long("other"));
        if fl.contains('U') { app = app.setting(AS::StrictUtf8); }
        let arg = app.p.opts[0].clone();
        let mut vals: Vec<OsString> = Vec::new();
        let v = f.get(2).cloned().unwrap_or("");
        if v.starts_with('#') {
            let p: Vec<u64> = v[1..].split(':').map(|x| x.parse().unwrap()).collect();
            let mut r = R(p[1].wrapping_mul(0x9E37_79B9_7F4A_7C15) | 1);
            for _ in 0..p[0] {
                let w: String = match pvs { Some(ref ps) => ps[r.below(ps.len() as u64) as usize].to_string(),
                                            None => WORDS[r.below(WORDS.len() as u64) as usize].to_string() };
                let w = if fl.contains('C') && pvs.is_some() {
                    w.chars().map(|c| if r.below(2) == 0 { c.to_ascii_uppercase() } else { c }).collect()
                } else { w };
                vals.push(OsString::from(w));
            }
            if p[2] == 1 {
                let bad = match r.below(5) {
                    0 => val("~"), 1 => OsString::from(""), 2 => OsString::from("a bad value"),
                    3 => OsString::from("x".repeat(50)), _ => OsString::from("not-a-possible-value"),
                };
                vals.push(bad);
            }
        } else if !v.is_empty() {
            for s in v.split('|') { vals.push(val(s)); }
        } else if !fl.contains('N') {
            vals.push(OsString::from(""));
        }
        let mut matcher = ArgMatcher::new();
        if !fl.contains('N') {
            for x in vals.iter() { matcher.add_val_to("opt", x); }
        }
        Case { app: app, arg: arg, ma: MatchedArg { occurs: 1, vals: vals }, matcher: matcher }
    }

    fn show(r: &ClapResult<()>) -> String {
        match *r { Ok(()) => "Ok".to_string(), Err(ref e) => format!("Err({:?}, {:?}, {:?})", e.kind, e.message, e.info) }
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let mut cases: Vec<Case> = read_lines().iter().map(|l| build(l)).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter_mut() {
                let r = Validator::new(&mut c.app.p).validate_arg_values(&c.arg, &c.ma, &c.matcher);
                fnv(&mut h, &format!("{}\n", show(&r)));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter_mut() {
                    let r = Validator::new(bb(&mut c.app.p)).validate_arg_values(bb(&c.arg), bb(&c.ma), &c.matcher);
                    acc = acc.wrapping_add(match r { Ok(()) => 1, Err(e) => e.message.len() as u64 });
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
