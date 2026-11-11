use std::env;
use std::io::{self, Read};

// Tiny WASI program: greets the first argument and counts lines,
// words and characters of whatever comes in on stdin.
fn main() {
    let name = env::args().nth(1).unwrap_or_else(|| "world".to_string());
    println!("Hello, {name}! (running as a WebAssembly job on WBX Sandbox)");

    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap_or(0);
    if !input.is_empty() {
        let lines = input.lines().count();
        let words = input.split_whitespace().count();
        let chars = input.chars().count();
        println!("stdin: {lines} lines, {words} words, {chars} characters");
    }
}
