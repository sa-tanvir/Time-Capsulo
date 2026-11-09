You are an expert Java developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Java code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```java code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `gson/src/main/java/com/google/gson/reflect/TypeToken.java`
- **Enclosing scope:** `public class TypeToken<T>`

## Imports / includes available in this file

```
import com.google.gson.internal.$Gson$Types;
import com.google.gson.internal.$Gson$Preconditions;
import java.lang.reflect.GenericArrayType;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.lang.reflect.TypeVariable;
import java.util.HashMap;
import java.util.Map;
```

## Other functions defined in the same file (signatures only; you may call them)

```
TypeToken::TypeToken( Type type)
TypeToken::TypeToken()
TypeToken::buildUnexpectedTypeError( Type token , Class <?> ... expected)
TypeToken::equals( Object o)
TypeToken::get( Class<T> type)
TypeToken::get( Type type)
TypeToken::getArray( Type componentType)
TypeToken::getParameterized( Type rawType , Type ... typeArguments)
TypeToken::getRawType()
TypeToken::getSuperclassTypeParameter( Class <?> subclass)
TypeToken::getType()
TypeToken::hashCode()
TypeToken::isAssignableFrom( Class <?> cls)
TypeToken::isAssignableFrom( Type from , GenericArrayType to)
TypeToken::isAssignableFrom( Type from)
TypeToken::isAssignableFrom( TypeToken <?> token)
TypeToken::matches( Type from , Type to , Map<String,Type> typeMap)
TypeToken::toString()
TypeToken::typeEquals( ParameterizedType from , ParameterizedType to , Map<String,Type> typeVarMap)
```

## Instance state

The method is `private static` and uses no instance state. Constants and siblings it relies on:

- `com.google.gson.internal.$Gson$Types.getRawType(Type)` (public static): the erased `Class<?>` of a `Class`, `ParameterizedType` (its raw type), `GenericArrayType` (the array class), `TypeVariable` (`Object.class`) or `WildcardType` (the raw type of its first upper bound); it throws `IllegalArgumentException` for any other `Type`.
- `typeEquals(ParameterizedType from, ParameterizedType to, Map<String, Type> typeVarMap)` (private static, `boolean`): `true` if both have the same raw type and every type argument of `from` matches the corresponding argument of `to`, where "matches" means equal (`to.equals(from)`) or `from`'s argument is a `TypeVariable` whose name is mapped in `typeVarMap` to a type equal to `to`'s argument.
- `matches(Type from, Type to, Map<String, Type> typeMap)` (private static, `boolean`): the per-argument test used by `typeEquals`.
- Java reflection: `Class.getGenericInterfaces()` (`Type[]`), `Class.getGenericSuperclass()` (`Type`, `null` for `Object`, interfaces, primitives), `Class.getTypeParameters()` (`TypeVariable<?>[]`), `ParameterizedType.getActualTypeArguments()` (`Type[]`), `TypeVariable.getName()`.

=== STUB ===
```java
private static boolean isAssignableFrom(Type from, ParameterizedType to,
    Map<String, Type> typeVarMap) {
    // TODO: implement according to the specification
}
```
