You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `read_varu32(data: &[u8]) -> (u32, usize)`

## 1. Component overview

Internal helper of the `regex` crate's lazy DFA. DFA states are stored compactly as byte strings in which
instruction pointers are written as variable-length integers (the LEB128 / Protocol Buffers "varint"
format, produced by the sibling `write_varu32`). `read_varu32` decodes **one** unsigned varint from the
start of `data` and reports how many bytes it occupied. It is called for every instruction pointer each
time a DFA state is expanded, so it is on a hot path of almost every regex search.

## 2. Functional requirements

1. A varint is a sequence of bytes in which every byte except the last has its high bit (`0x80`) set; the
   first byte whose high bit is clear terminates it.
2. The value is assembled little-endian, 7 bits per byte: the low 7 bits of byte `i` (0-based) contribute
   `(byte_i & 0x7F) << (7 * i)`.
3. Return `(value, k)` where `k` is the number of bytes consumed, i.e. the index of the terminating byte
   plus one. Bytes after the terminator are ignored.
4. If `data` contains no terminating byte (empty input, or every byte has the high bit set), return
   `(0, 0)`.
5. Redundant (non-minimal) encodings are accepted: e.g. `[0x80, 0x00]` decodes to `(0, 2)` and
   `[0x81, 0x80, 0x00]` to `(1, 3)`.

Examples:

| `data` (hex) | result |
|---|---|
| `00` | `(0, 1)` |
| `01` | `(1, 1)` |
| `7f` | `(127, 1)` |
| `80 01` | `(128, 2)` |
| `ac 02` | `(300, 2)` |
| `ff ff 03` | `(65535, 3)` |
| `ff ff ff 7f` | `(268435455, 4)` |
| `ff ff ff ff 0f` | `(4294967295, 5)` |
| `0a 0b` | `(10, 1)` |
| `96 01 02 03` | `(150, 2)` |
| (empty) | `(0, 0)` |
| `80`, `ff ff ff ff` | `(0, 0)` |

Property (tested): for every `n: u32`, writing `n` with `write_varu32` into an empty buffer and reading it
back yields `(n, buffer.len())`. The signed variant `read_vari32` relies on this function and must
round-trip every `i32` as well.

## 3. Input specification

- `data: &[u8]`: any length. Inputs in this crate always encode a value that fits in `u32`, so a
  terminated varint never has more than 5 bytes; longer encodings do not occur and need not be handled.

## 4. Output specification

- `(u32, usize)`: decoded value and number of bytes consumed (1–5), or `(0, 0)` if unterminated.

## 5. Edge cases and constraints

- Pure function; no allocation; no mutation; must not read past the terminating byte or past `data`.
- Typically called in a loop that advances through a buffer by the returned length until it gets 0.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/dfa.rs`

## Imports / includes available in this file

```
use std::collections::HashMap;
use std::fmt;
use std::iter::repeat;
use std::mem;
use exec::ProgramCache;
use prog::{Inst, Program};
use sparse::SparseSet;
    use prog::Inst::*;
        use prog::Inst::*;
        use prog::Inst::*;
        use prog::EmptyLook::*;
        use prog::Inst::*;
    use std::ascii::escape_default;
    use quickcheck::{QuickCheck, StdGen, quickcheck};
    use super::{
        StateFlags, State, push_inst_ptr,
        write_varu32, read_varu32, write_vari32, read_vari32,
    };
```

## Other functions defined in the same file (signatures only; you may call them)

```
(Vec<u32>,u8)->
(i32)->
(u32)->
add & mut self
add_state & mut self , state : State
approximate_size & self
as_byte & self
byte b : u8
byte_class & self , b : Byte
cached_state & mut self , q : & SparseSet , mut state_flags : StateFlags , current_state : Option < & mut StatePtr > ,
cached_state_key & mut self , q : & SparseSet , state_flags : & mut StateFlags ,
can_exec insts : & Program
clear & mut self
clear_cache & mut self
clear_cache_and_save & mut self , current_state : Option < & mut StatePtr > ,
continue_past_first_match & self
eof
exec_at & mut self , qcur : & mut SparseSet , qnext : & mut SparseSet , text : & [ u8 ] ,
exec_at_reverse & mut self , qcur : & mut SparseSet , qnext : & mut SparseSet , text : & [ u8 ] ,
exec_byte & mut self , qcur : & mut SparseSet , qnext : & mut SparseSet , mut si : StatePtr , b : Byte ,
flags & self
fmt & self , f : & mut fmt :: Formatter
follow_epsilons & mut self , ip : InstPtr , q : & mut SparseSet , flags : EmptyFlags ,
forward prog : & a Program , cache : & ProgramCache , quit_after_match : bool , text : & [ u8 ] , at : usize ,
forward_many prog : & a Program , cache : & ProgramCache , matches : & mut [ bool ] , text : & [ u8 ] , at : usize ,
has_empty & self
has_prefix & self
inst_ptrs & self
is_ascii_word & self
is_eof & self
is_match & self
is_word & self
map self , mut f : F
new num_byte_classes : usize
new prog : & Program
next & mut self
next & self , si : StatePtr , cls : usize
next_si & self , si : StatePtr , text : & [ u8 ] , i : usize
next_state & mut self , qcur : & mut SparseSet , qnext : & mut SparseSet , si : StatePtr , b : Byte ,
next_unchecked & self , si : StatePtr , cls : usize
num_byte_classes & self
num_states & self
p ips : Vec < u32 > , flags : u8
p n : i32
p n : u32
prefix_at & self , text : & [ u8 ] , at : usize
push_inst_ptr data : & mut Vec < u8 > , prev : & mut InstPtr , ip : InstPtr
read_vari32 data : & [ u8 ]
reset_size & mut self
restore_state & mut self , state : State
reverse prog : & a Program , cache : & ProgramCache , quit_after_match : bool , text : & [ u8 ] , at : usize ,
set_empty & mut self
set_match & mut self
set_next & mut self , si : StatePtr , cls : usize , next : StatePtr
set_non_match self , at : usize
set_word & mut self
show_state_ptr si : StatePtr
start_flags & self , text : & [ u8 ] , at : usize
start_flags_reverse & self , text : & [ u8 ] , at : usize ,
start_ptr & self , si : StatePtr
start_state & mut self , q : & mut SparseSet , empty_flags : EmptyFlags , state_flags : StateFlags ,
state & self , si : StatePtr
state_heap_size & self
u8_class & self , b : u8
usize_to_u32 n : usize
vb b : usize
write_vari32 data : & mut Vec < u8 > , n : i32
write_varu32 data : & mut Vec < u8 > , mut n : u32
```

## Sibling functions (same file)

- `write_varu32(data: &mut Vec<u8>, n: u32)`: appends `n` in LEB128 form (7 bits per byte, least significant group
  first, high bit set on every byte but the last; minimal length).
- `read_vari32(data: &[u8]) -> (i32, usize)` / `write_vari32`: zig-zag signed variants built on `read_varu32` /
  `write_varu32`.

=== STUB ===
```rust
fn read_varu32(data: &[u8]) -> (u32, usize) {
    // TODO: implement according to the specification
}
```
