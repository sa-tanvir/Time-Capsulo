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
