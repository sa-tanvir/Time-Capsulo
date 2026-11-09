# Functional specification: `func (t Result) arrayOrMap(vc byte, valueize bool) (r arrayOrMapResult)`

## 1. Component overview

`arrayOrMap` is an internal method of `gjson.Result` in the `gjson` package
(`github.com/tidwall/gjson`), a library that reads values out of JSON text
without fully decoding it. It lists the members of the JSON array or object
whose raw text is `t.Raw`. It backs three public methods:

- `Result.Array()` calls `t.arrayOrMap('[', false)` and returns `r.a`;
- `Result.Map()` calls `t.arrayOrMap('{', false)` and returns `r.o`;
- `Result.Value()` calls `t.arrayOrMap(0, true)` and returns `r.oi` or `r.ai`
  depending on `r.vc` (so `Value()` and `arrayOrMap` are mutually recursive for
  nested containers).

The result type `arrayOrMapResult` (fields `a`, `ai`, `o`, `oi`, `vc`) and the
helpers `tonum`, `tolit`, `tostr`, `squash` and `Value` are described in the
context. Only `t.Raw` is read; `t.Type` and the other fields are ignored.

## 2. Functional requirements

1. **Finding the container.** Skip leading bytes `<= ' '` of `t.Raw`.
   - `vc == 0`: the first other byte must be `{` or `[`; it becomes `r.vc`.
   - `vc != 0` (`'['` or `'{'`): the first other byte must equal `vc`;
     `r.vc = vc`.
   - If the first non-whitespace byte does not qualify (e.g. `"asdf"`,
     `**invalid**`, or `[` when `vc == '{'`), return the **zero**
     `arrayOrMapResult` (all four collections `nil`, `vc == 0`).
   - If `t.Raw` is empty or only whitespace, there is no failure: `r.vc` is
     `vc` (so 0 when `vc == 0`) and an empty collection is created as in
     rule 2.
2. **Exactly one collection is allocated** (empty but non-nil), the others stay
   `nil`: if `r.vc == '{'` then `oi` (when `valueize`) or `o` (otherwise);
   in every other case `ai` (when `valueize`) or `a`.
3. **Tokens.** After the opening bracket, scan the rest of `t.Raw`:
   - bytes `<= ' '` are skipped;
   - the first `]` or `}` (of either kind) found between tokens ends the scan;
   - a token starts at a digit or `-` (Number: `Raw, Num = tonum(...)`,
     `Str = ""`), `{` or `[` (JSON: `Raw = squash(...)`, `Str = ""`, `Num = 0`),
     `"` (String: `Raw, Str = tostr(...)`, `Num = 0`), `t` (True), `f` (False),
     or `n` (Null) — the last three with `Raw = tolit(...)`, `Str = ""`,
     `Num = 0`. Each helper is applied to the text starting at the token;
   - any other byte (`,`, `:`, stray letters, ...) is skipped;
   - scanning continues right after the token's `Raw`;
   - every token `Result` has `Index = 0`.
4. **Arrays** (`r.vc != '{'`): every token is appended in order to `a`, or, when
   `valueize`, `token.Value()` is appended to `ai`.
5. **Objects** (`r.vc == '{'`): tokens alternate key, value, key, value, ... by
   position (the 1st, 3rd, 5th ... token is a key, whatever its type). The
   member name is the key token's `Str` (so `""` for a non-string key). For
   each value token, the pair is stored only if the name is **not already
   present** (the first occurrence of a duplicate key wins): in `o` as the
   token `Result`, or, when `valueize`, in `oi` as `token.Value()`. A final key
   without a value is ignored.
6. **Value conversion** (`valueize`): `Value()` gives `string` for String,
   `float64` for Number, `bool` for True/False, `nil` for Null, and for JSON
   tokens a nested `map[string]interface{}` / `[]interface{}` built by the same
   rules.
7. The function does not modify `t`; safe for concurrent use. It must not panic
   for any `Raw` text.

## 3. Input specification

- `t`: any `Result`; only `t.Raw` is used. It is normally the raw text of a JSON
  object or array (possibly with leading whitespace, raw UTF-8, escapes), but may
  be malformed or empty.
- `vc`: `0`, `'['` (91) or `'{'` (123).
- `valueize`: whether to fill the `ai`/`oi` (Go values) instead of `a`/`o`
  (`Result`s).

## 4. Output specification

- `arrayOrMapResult` with `vc` and exactly one non-nil collection (or none, for
  the zero result) as described.

## 5. Edge cases and constraints

`vc` shown as a character; `o`/`a` contents shown as Raw texts.

- `**invalid**`, any `vc` -> zero result. `"asdf"`, any `vc` -> zero result.
- `[` with `vc='{'`, or `{...}` with `vc='['` -> zero result.
- `{` with `vc=0` or `'{'` -> `vc='{'`, `o` = empty map (or `oi` = empty map).
- `""` or `"   "`: `vc=0` -> `vc=0`, `a` = empty slice; `vc='{'` -> `vc='{'`,
  `o` = empty map; `vc='['` -> `vc='['`, `a` = empty slice.
- `[]` -> `vc='['`, empty `a`; `{}` -> `vc='{'`, empty `o`.
- `{"asdf":"ghjk"` (unterminated) -> `o = {"asdf": "ghjk"}`.
- `{"name": "Alex","name": "Peter"}` -> `o = {"name": "Alex"}` (first wins).
- `{"array": ["PERSON1","PERSON2",0],}` -> `o = {"array": <JSON ["PERSON1","PERSON2",0]>}`;
  with `valueize`: `oi = {"array": ["PERSON1", "PERSON2", 0.0]}`.
- `[1,[2,3],{"a":"b"},true,false,null,"s\"q"]` -> seven Results:
  Number `1` (Num 1), JSON `[2,3]`, JSON `{"a":"b"}`, True `true`, False `false`,
  Null `null`, String `"s\"q"` (Str `s"q`); with `valueize`:
  `[1, [2, 3], {"a": "b"}, true, false, nil, "s\"q"]`.
- ` \n [ "é", -1.5e3, 1e400 ] ` -> Str `é`, Num -1500, Num +Inf.
- `[x, 1]` -> one element `1` (the `x` is skipped). `[1 2 3]` -> `1`, `2`, `3`.
- `[nul, tru, fals]` -> Null `nul`, True `tru`, False `fals`.
- `[-, -1, 0.5e-3, 5E+2]` -> Numbers with Raw `-` (Num 0), `-1`, `0.5e-3`, `5E+2`.
- `{"a":-}` -> `o = {"a": Number "-" (Num 0)}`.
- `{"a" "b" "c" "d"}` -> `o = {"a": "b", "c": "d"}` (separators are not required).
- `{"a":1,"b"}` -> `o = {"a": 1}`.
- `{1:2,true:3}` -> `tonum` reads `1:2` as one Number token (key, name `""`),
  `true` is its value, `3` a dangling key: `o = {"": True}`.
- `{"k":[1,2,3}` -> `o = {"k": JSON "[1,2,3}"}`; with `valueize` `{"k": [1, 2, 3]}`.
- `{"":1,"":2}` -> `o = {"": 1}`.
- `{"a":{"b":[1,2]},"c":"]"}` -> `o = {"a": JSON {"b":[1,2]}, "c": String "]"}`.
- Runs in time linear in `len(t.Raw)` when `valueize` is false.
