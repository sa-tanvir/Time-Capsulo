# Functional specification

## 1. Component overview

`TypeToken.isAssignableFrom(from, to, typeVarMap)` is the recursive helper that decides whether a value of generic type `from` can be assigned to the parameterized type `to` (for example whether `ArrayList<String>` is assignable to `Collection<String>`), by walking the generic supertypes of `from` and comparing type arguments. `typeVarMap` records what the type variables seen so far stand for.

## 2. Functional requirements

Return `true` iff `to` is found among `from` and its generic supertypes, in this sense:

1. If `from` is `null`: return `false`.
2. If `to.equals(from)`: return `true`.
3. Let `clazz` be the raw class of `from` (`$Gson$Types.getRawType(from)`) and, when `from` is itself a `ParameterizedType`, `ptype = from`.
4. If `ptype` exists: pair each actual type argument of `ptype` with the corresponding type parameter of `clazz` (by position) and **record** in `typeVarMap`: parameter name -> argument. When an actual argument is itself a `TypeVariable`, first replace it by what `typeVarMap` currently maps its name to, repeating while the replacement is a `TypeVariable` (if the name is not mapped, the replacement is `null` and is recorded as such). The recording is visible to the caller: `typeVarMap` is modified in place. Afterwards, if `typeEquals(ptype, to, typeVarMap)` is true, return `true`.
5. Then try each generic interface of `clazz` (`getGenericInterfaces()`, in declaration order): if the same question (interface type, `to`) is answered `true` with a **copy** of the current `typeVarMap` (changes made while exploring a supertype are not propagated back to the caller's map), return `true`.
6. Otherwise answer the same question for the generic superclass of `clazz` (`getGenericSuperclass()`), again with a copy of `typeVarMap`, and return that answer. A missing superclass (`null`: for `Object`, interfaces, primitive and similar classes) gives `false` by rule 1.

## 3. Input specification

- `from` (`Type`): any `Type` (class, parameterized type, generic array, type variable, wildcard) or `null`.
- `to` (`ParameterizedType`): the target type, non-null.
- `typeVarMap` (`Map<String, Type>`): mutable map from type-variable names to types; typically empty on the first call; may be pre-filled (for example `T -> String`). It may hold `null` values after the call.
- Hierarchies may be up to dozens of levels deep, each level adding an interface and a superclass.

## 4. Output specification

`boolean`, plus the update of `typeVarMap` described in rule 4 (for the top-level call: the entries recorded for `from` itself when it is parameterized; the entries recorded while exploring supertypes are not visible). Examples:

- `from = List<String>`, `to = List<String>`: `true` (rule 2).
- `from = ArrayList<String>`, `to = Collection<String>`: `true`; `to = List<Integer>`: `false`.
- `from = List<Integer>`, `to = List<Number>`: `false` (arguments must be equal).
- `from = B<String>` where `class B<U> extends A<List<U>>`, `to = A<List<String>>`: `true`; `to = A<List<Integer>>`: `false`.
- `from = String` (a raw class), `to = Comparable<String>`: `true`; `to = Comparable<Integer>`: `false`.
- `from = null`: `false`.

## 5. Edge cases and constraints

- The map passed in is changed only by rule 4 for `from` itself (as described); the exploration of supertypes works on copies.
- `from` of a kind for which `$Gson$Types.getRawType` throws (not a class, parameterized type, generic array, variable or wildcard) propagates that exception (`IllegalArgumentException`).
- Running time grows with the depth of the hierarchy of `from` (each level is explored once per path; interface hierarchies can be explored repeatedly).
- Not thread-safe with respect to `typeVarMap`.
