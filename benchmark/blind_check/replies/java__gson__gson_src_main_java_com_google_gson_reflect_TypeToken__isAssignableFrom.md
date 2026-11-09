```java
private static boolean isAssignableFrom(Type from, ParameterizedType to,
    Map<String, Type> typeVarMap) {
    if (from == null) {
        return false;
    }

    if (to.equals(from)) {
        return true;
    }

    Class<?> clazz = $Gson$Types.getRawType(from);
    ParameterizedType ptype = null;
    if (from instanceof ParameterizedType) {
        ptype = (ParameterizedType) from;
    }

    if (ptype != null) {
        Type[] tArgs = ptype.getActualTypeArguments();
        TypeVariable<?>[] tParams = clazz.getTypeParameters();
        for (int i = 0; i < tArgs.length; i++) {
            Type arg = tArgs[i];
            TypeVariable<?> var = tParams[i];
            while (arg instanceof TypeVariable) {
                TypeVariable<?> v = (TypeVariable<?>) arg;
                arg = typeVarMap.get(v.getName());
            }
            typeVarMap.put(var.getName(), arg);
        }

        if (typeEquals(ptype, to, typeVarMap)) {
            return true;
        }
    }

    for (Type itype : clazz.getGenericInterfaces()) {
        if (isAssignableFrom(itype, to, new HashMap<String, Type>(typeVarMap))) {
            return true;
        }
    }

    Type sType = clazz.getGenericSuperclass();
    return isAssignableFrom(sType, to, new HashMap<String, Type>(typeVarMap));
}
```
