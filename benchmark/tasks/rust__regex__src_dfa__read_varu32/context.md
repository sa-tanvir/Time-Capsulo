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
