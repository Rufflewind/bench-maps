extern crate rand;
extern crate time;

use std::collections::{BTreeMap, HashMap};
use rand::Rng;
use rand::distributions::IndependentSample;
use time::precise_time_ns;

trait Map {

    fn len(&mut self) -> usize;

    fn insert(&mut self, key: i64, value: i64) -> Option<i64>;

    fn get(&mut self, key: &i64) -> Option<&i64>;
}

impl Map for BTreeMap<i64, i64> {

    fn len(&mut self) -> usize {
        BTreeMap::len(self)
    }

    fn insert(&mut self, key: i64, value: i64) -> Option<i64> {
        BTreeMap::insert(self, key, value)
    }

    fn get(&mut self, key: &i64) -> Option<&i64> {
        BTreeMap::get(self, key)
    }
}

impl Map for HashMap<i64, i64> {

    fn len(&mut self) -> usize {
        HashMap::len(self)
    }

    fn insert(&mut self, key: i64, value: i64) -> Option<i64> {
        HashMap::insert(self, key, value)
    }

    fn get(&mut self, key: &i64) -> Option<&i64> {
        HashMap::get(self, key)
    }
}

fn bench<M: Map, R: Rng>(m: &mut M, max: i64, repeats: i64, count: i64, rng: &mut R) {
    let uniform = rand::distributions::Range::new(0, max);
    let mut sum: u8 = 0;

    println!("{{ \"insert\":\n[ [\"iter\", \"size\", \"time\"]");
    for k in 0 .. count {
        let t0 = precise_time_ns();
        for _ in 0 .. repeats {
            let k = uniform.ind_sample(rng);
            m.insert(k, k - 1);
        }
        let t = (precise_time_ns() - t0) as f64 * 1e-9;
        println!(", [{}, {}, {}]", (k + 1) * repeats, m.len(), t);
    }

    println!("]\n, \"lookup\":\n[ [\"iter\", \"misses\", \"time\"]");
    for k in 0 .. count {
        let mut misses = 0;
        let t0 = precise_time_ns();
        for _ in 0 .. repeats {
            let k = uniform.ind_sample(rng);
            match m.get(&k) {
                None => {
                    misses += 1;
                }
                Some(v) => {
                    sum = sum.wrapping_add(*v as u8);
                }
            }
        }
        let t = (precise_time_ns() - t0) as f64 * 1e-9;
        println!(", [{}, {}, {}]", (k + 1) * repeats, misses, t);
    }

    println!("]\n, \"rng\":\n[ [\"time\"]");
    for _ in 0 .. count {
        let t0 = precise_time_ns();
        for _ in 0 .. repeats {
            let k = uniform.ind_sample(rng);
            sum = sum.wrapping_add(k as u8);
        }
        let t = (precise_time_ns() - t0) as f64 * 1e-9;
        println!(", [{}]", t);
    }

    println!("]\n}}\n//ignore this: {}", sum);
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let max: i64 = args[1].parse().unwrap();
    let repeats: i64 = args[2].parse().unwrap();
    let count: i64 = args[3].parse().unwrap();

    let mut rng = rand::thread_rng();
    println!("{{ \"_lang\": \"rs\", \"BTreeMap\":");
    {
        let mut m = BTreeMap::new();
        bench(&mut m, max, repeats, count, &mut rng);
    }
    println!(", \"HashMap\":");
    {
        let mut m = HashMap::new();
        bench(&mut m, max, repeats, count, &mut rng);
    }
    println!("}}");
}
