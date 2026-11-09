
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `find_cap_ref`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use std::time::Instant;

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
    }

    fn load() -> Vec<(usize, Vec<u8>)> {
        let task = ::std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = ::std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = ::std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            (f[0].parse().unwrap(), unhex(f.get(1).cloned().unwrap_or("")))
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
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let s = match find_cap_ref(&c.1[..]) {
                    None => "None".to_string(),
                    Some(r) => match r.cap {
                        Ref::Named(n) => format!("N:{}:{}", n, r.end),
                        Ref::Number(i) => format!("I:{}:{}", i, r.end),
                    },
                };
                fnv(&mut h, &format!("{}\n", s));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    for _ in 0..c.0 {
                        let x: &[u8] = bb(&c.1[..]);
                        acc = acc.wrapping_add(match find_cap_ref(x) {
                            None => 1,
                            Some(r) => r.end as u64 + match r.cap { Ref::Named(n) => n.len() as u64, Ref::Number(i) => i as u64 },
                        });
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
