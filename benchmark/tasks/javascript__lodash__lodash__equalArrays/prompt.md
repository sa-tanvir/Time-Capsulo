You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `equalArrays(array, other, bitmask, customizer, equalFunc, stack)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14's deep-equality engine (`_.isEqual`,
`_.isEqualWith`, `_.isMatch`, `_.isMatchWith`, `_.matches`, `_.matchesProperty`).
`baseIsEqualDeep` calls it to compare two arrays, two typed arrays or two
buffers, and the map/set branch of `equalByTag` calls it with the entry lists of
two maps (`[key, value]` pairs) or the value lists of two sets. It compares the
elements index by index (or, in *unordered* mode, by finding a distinct partner
for every element), recursing into nested values through `equalFunc`, and it
supports *partial* comparison (used by `_.isMatch`), a user customizer, and
circular references via `stack`.

## 2. Functional requirements

Flags in `bitmask`: `COMPARE_PARTIAL_FLAG` (1) and `COMPARE_UNORDERED_FLAG` (2).

1. **Length.** Let `n = array.length` and `m = other.length`. If `n != m`, return
   `false`, except in partial mode where `m > n` is allowed (`other` may have
   extra elements).
2. **Cycles.** If `stack.get(array)` is truthy **and** `stack.get(other)` is
   truthy, the pair is already being compared further up: return whether
   `stack.get(array) == other`, without examining elements.
3. Otherwise record the pair in both directions (`stack.set(array, other)` and
   `stack.set(other, array)`), compare the elements, then remove both entries
   with `stack['delete'](array)` and `stack['delete'](other)` before returning,
   whatever the outcome (also after an early mismatch).
4. **Elements.** For each index `i` from `0` to `n - 1` in order (non-index
   properties are ignored; holes read as `undefined`), with `a = array[i]` and
   `o = other[i]`:
   - If `customizer` is given, call it first: in partial mode as
     `customizer(o, a, i, other, array, stack)`, otherwise as
     `customizer(a, o, i, array, other, stack)`. If it returns anything other than
     `undefined`, a truthy value means "element equal, go on" and a falsy value
     means "not equal": the result is `false` and comparison stops.
   - Otherwise (no customizer, or it returned `undefined`):
     - **ordered mode** (unordered flag not set): the element matches when
       `a === o` or `equalFunc(a, o, bitmask, customizer, stack)` is truthy;
     - **unordered mode**: scan **all** of `other` (indices `0 .. m - 1`, in
       order) for the first index `j` not yet claimed by an earlier element of
       `array` such that `a === other[j]` or
       `equalFunc(a, other[j], bitmask, customizer, stack)`; claim `j` (each index
       of `other` can be claimed at most once) and continue. If no such `j`
       exists, the element does not match.
     If the element does not match, the result is `false` and comparison stops.
5. Return `true` if every element matched, otherwise `false` (a primitive
   boolean).

## 3. Input specification

- `array`, `other`: arrays (possibly sparse, possibly with extra non-index
  properties, possibly containing themselves), typed arrays, buffers, or the
  converted entry/value arrays of maps/sets. Contents are arbitrary values.
- `bitmask`: integer combining the two flags above (0 for `_.isEqual`; partial and
  unordered for `_.isMatch`; unordered is added for map/set contents).
- `customizer`: optional function; its return value is interpreted as above.
- `equalFunc`: the recursive deep-equality function
  `(value, other, bitmask, customizer, stack) => boolean` (normally `baseIsEqual`).
- `stack`: a `Stack` instance (key/value cache with `get`, `set`, `has`,
  `delete`) shared by the whole comparison.

## 4. Output specification

`true` or `false`. Examples through the public API:

- `isEqual([1, 'a', {e: 1}], [1, 'a', {e: 1}])` -> `true`;
  `isEqual([1, 2, 3], [3, 2, 1])` -> `false`; `isEqual([1, 2], [1, 2, 3])` -> `false`
- `isEqual(Array(1), [undefined])` -> `true` (sparse arrays compare as dense)
- arrays with identical elements but different extra properties
  (`a.b = 1` vs `a.b = 2`) -> `true`
- `var a = [1]; a[1] = a; var b = [1]; b[1] = b;` -> `isEqual(a, b)` is `true`;
  pushing different values afterwards makes them unequal
- typed arrays / buffers with equal elements and the same type -> `true`
- `isEqual(new Set([1, 2]), new Set([2, 1]))` -> `true` (unordered);
  maps with the same entries in different insertion order -> `true`
- partial (`_.isMatch`): `isMatch({a: [1, 2, 3]}, {a: [3, 1]})` -> `true`;
  `isMatch({a: [1, 2]}, {a: [2, 2]})` -> `false` (each element of `other` can
  be used only once); `isMatch({a: [1, 2]}, {a: []})` -> `true`
- `isEqualWith(['a'], ['b'], v => typeof v == 'string' || undefined)` -> `true`;
  with a customizer returning `false` for strings, `isEqualWith(['a'], ['a'], c)`
  is `false`; a customizer returning `undefined` changes nothing
- `isEqualWith` customizer receives, for array elements, exactly
  `(a[i], o[i], i, array, other, stack)`

## 5. Edge cases and constraints

- Must not mutate `array` or `other`; the only side effects are on `stack`
  (always restored) and calls to `customizer`/`equalFunc`.
- Stop at the first mismatch (no further customizer or `equalFunc` calls).
- Strict identity (`===`) of two elements is enough for a match without calling
  `equalFunc`; `NaN` handling is left to `equalFunc`.
- Ordered comparison is linear in `n` (plus nested work); unordered comparison
  may be quadratic.

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `lodash.js`
- **Enclosing scope:** the function is defined inside `runInContext(context)` in lodash.js (lodash 4.17.14, a single file wrapped in an IIFE); every function and value listed below is in scope by its bare name. Public methods are also attached to the `lodash` (`_`) object.

## Imports / includes available in this file

```
(none)
```

## Helpers and values most relevant to this function

Documentation summaries copied from lodash.js; signatures only.

- `SetCache(values)`: Creates an array cache object to store unique values.
- `arraySome(array, predicate)`: A specialized version of `_.some` for arrays without support for iteratee shorthands.
- `cacheHas(cache, key)`: Checks if a `cache` value for `key` exists.

Values (declarations as in lodash.js):

```
var COMPARE_PARTIAL_FLAG = 1;
var COMPARE_UNORDERED_FLAG = 2;
```

## Cache classes defined in lodash.js (constructors; use with `new`)

- `Stack([entries])`: key/value cache used to track visited objects. Methods:
  `get(key)` (value or `undefined`), `set(key, value)` (returns the stack),
  `has(key)`, `delete(key)` (call it as `stack['delete'](key)` for old-engine
  compatibility), `clear()`. Keys may be any value (objects by identity), compared
  with SameValueZero.
- `SetCache([values])`: set of unique values. Methods: `add(value)` / `push(value)`
  (alias), `has(value)`; membership by SameValueZero (`NaN` matches `NaN`,
  `-0` matches `0`). `cacheHas(cache, key)` is `cache.has(key)`.


## All named functions defined in lodash.js (signatures only; you may call them)

```
Hash(entries)
LazyWrapper(value)
ListCache(entries)
LodashWrapper(value, chainAll)
MapCache(entries)
SetCache(values)
Stack(entries)
add(augend, addend)
after(n, func)
apply(func, thisArg, args)
arrayAggregator(array, setter, iteratee, accumulator)
arrayEach(array, iteratee)
arrayEachRight(array, iteratee)
arrayEvery(array, predicate)
arrayFilter(array, predicate)
arrayIncludes(array, value)
arrayIncludesWith(array, value, comparator)
arrayLikeKeys(value, inherited)
arrayMap(array, iteratee)
arrayPush(array, values)
arrayReduce(array, iteratee, accumulator, initAccum)
arrayReduceRight(array, iteratee, accumulator, initAccum)
arraySample(array)
arraySampleSize(array, n)
arrayShuffle(array)
arraySome(array, predicate)
ary(func, n, guard)
asciiToArray(string)
asciiWords(string)
assign(object, sources)
assignIn(object, sources)
assignInWith(object, sources, customizer)
assignMergeValue(object, key, value)
assignValue(object, key, value)
assignWith(object, sources, customizer)
assocIndexOf(array, key)
at(object, paths)
attempt(func, args)
baseAggregator(collection, setter, iteratee, accumulator)
baseAssign(object, source)
baseAssignIn(object, source)
baseAssignValue(object, key, value)
baseAt(object, paths)
baseClamp(number, lower, upper)
baseClone(value, bitmask, customizer, key, object, stack)
baseConforms(source)
baseConformsTo(object, source, props)
baseDelay(func, wait, args)
baseDifference(array, values, iteratee, comparator)
baseEach(collection, iteratee)
baseEachRight(collection, iteratee)
baseEvery(collection, predicate)
baseExtremum(array, iteratee, comparator)
baseFill(array, value, start, end)
baseFilter(collection, predicate)
baseFindIndex(array, predicate, fromIndex, fromRight)
baseFindKey(collection, predicate, eachFunc)
baseFlatten(array, depth, predicate, isStrict, result)
baseFor(object, iteratee, keysFunc)
baseForOwn(object, iteratee)
baseForOwnRight(object, iteratee)
baseForRight(object, iteratee, keysFunc)
baseFunctions(object, props)
baseGet(object, path)
baseGetAllKeys(object, keysFunc, symbolsFunc)
baseGetTag(value)
baseGt(value, other)
baseHas(object, key)
baseHasIn(object, key)
baseInRange(number, start, end)
baseIndexOf(array, value, fromIndex)
baseIndexOfWith(array, value, fromIndex, comparator)
baseIntersection(arrays, iteratee, comparator)
baseInverter(object, setter, iteratee, accumulator)
baseInvoke(object, path, args)
baseIsArguments(value)
baseIsArrayBuffer(value)
baseIsDate(value)
baseIsEqual(value, other, bitmask, customizer, stack)
baseIsEqualDeep(object, other, bitmask, customizer, equalFunc, stack)
baseIsMap(value)
baseIsMatch(object, source, matchData, customizer)
baseIsNaN(value)
baseIsNative(value)
baseIsRegExp(value)
baseIsSet(value)
baseIsTypedArray(value)
baseIteratee(value)
baseKeys(object)
baseKeysIn(object)
baseLodash()
baseLt(value, other)
baseMap(collection, iteratee)
baseMatches(source)
baseMatchesProperty(path, srcValue)
baseMean(array, iteratee)
baseMerge(object, source, srcIndex, customizer, stack)
baseMergeDeep(object, source, key, srcIndex, mergeFunc, customizer, stack)
baseNth(array, n)
baseOrderBy(collection, iteratees, orders)
basePick(object, paths)
basePickBy(object, paths, predicate)
baseProperty(key)
basePropertyDeep(path)
basePropertyOf(object)
basePullAll(array, values, iteratee, comparator)
basePullAt(array, indexes)
baseRandom(lower, upper)
baseRange(start, end, step, fromRight)
baseReduce(collection, iteratee, accumulator, initAccum, eachFunc)
baseRepeat(string, n)
baseRest(func, start)
baseSample(collection)
baseSampleSize(collection, n)
baseSet(object, path, value, customizer)
baseShuffle(collection)
baseSlice(array, start, end)
baseSome(collection, predicate)
baseSortBy(array, comparer)
baseSortedIndex(array, value, retHighest)
baseSortedIndexBy(array, value, iteratee, retHighest)
baseSortedUniq(array, iteratee)
baseSum(array, iteratee)
baseTimes(n, iteratee)
baseToNumber(value)
baseToPairs(object, props)
baseToString(value)
baseUnary(func)
baseUniq(array, iteratee, comparator)
baseUnset(object, path)
baseUpdate(object, path, updater, customizer)
baseValues(object, props)
baseWhile(array, predicate, isDrop, fromRight)
baseWrapperValue(value, actions)
baseXor(arrays, iteratee, comparator)
baseZipObject(props, values, assignFunc)
before(n, func)
bind(func, thisArg, partials)
bindAll(object, methodNames)
bindKey(object, key, partials)
cacheHas(cache, key)
camelCase(string)
capitalize(string)
castArray()
castArrayLikeObject(value)
castFunction(value)
castPath(value, object)
castRest(func)
castSlice(array, start, end)
ceil(number, precision)
chain(value)
charsEndIndex(strSymbols, chrSymbols)
charsStartIndex(strSymbols, chrSymbols)
chunk(array, size, guard)
clamp(number, lower, upper)
clone(value)
cloneArrayBuffer(arrayBuffer)
cloneBuffer(buffer, isDeep)
cloneDataView(dataView, isDeep)
cloneDeep(value)
cloneDeepWith(value, customizer)
cloneRegExp(regexp)
cloneSymbol(symbol)
cloneTypedArray(typedArray, isDeep)
cloneWith(value, customizer)
compact(array)
compareAscending(value, other)
compareMultiple(object, other, orders)
composeArgs(args, partials, holders, isCurried)
composeArgsRight(args, partials, holders, isCurried)
concat()
cond(pairs)
conforms(source)
conformsTo(object, source)
constant(value)
copyArray(source, array)
copyObject(source, props, object, customizer)
copySymbols(source, object)
copySymbolsIn(source, object)
countBy(collection)
countHolders(array, placeholder)
create(prototype, properties)
createAggregator(setter, initializer)
createAssigner(assigner)
createBaseEach(eachFunc, fromRight)
createBaseFor(fromRight)
createBind(func, bitmask, thisArg)
createCaseFirst(methodName)
createCompounder(callback)
createCtor(Ctor)
createCurry(func, bitmask, arity)
createFind(findIndexFunc)
createFlow(fromRight)
createHybrid(func, bitmask, thisArg, partials, holders, partialsRight, holdersRight, argPos, ary, arity)
createInverter(setter, toIteratee)
createMathOperation(operator, defaultValue)
createOver(arrayFunc)
createPadding(length, chars)
createPartial(func, bitmask, thisArg, partials)
createRange(fromRight)
createRecurry(func, bitmask, wrapFunc, placeholder, thisArg, partials, holders, argPos, ary, arity)
createRelationalOperation(operator)
createRound(methodName)
createToPairs(keysFunc)
createWrap(func, bitmask, thisArg, partials, holders, argPos, ary, arity)
curry(func, arity, guard)
curryRight(func, arity, guard)
customDefaultsAssignIn(objValue, srcValue, key, object)
customDefaultsMerge(objValue, srcValue, key, object, source, stack)
customOmitClone(value)
debounce(func, wait, options)
deburr(string)
defaultTo(value, defaultValue)
defaults(object, sources)
defaultsDeep(object, sources)
defer(func, args)
delay(func, wait, args)
difference(array, values)
differenceBy(array, values)
differenceWith(array, values, comparator)
divide(dividend, divisor)
drop(array, n, guard)
dropRight(array, n, guard)
dropRightWhile(array, predicate)
dropWhile(array, predicate)
endsWith(string, target, position)
eq(value, other)
equalByTag(object, other, tag, bitmask, customizer, equalFunc, stack)
equalObjects(object, other, bitmask, customizer, equalFunc, stack)
escape(string)
escapeRegExp(string)
escapeStringChar(chr)
every(collection, predicate, guard)
fill(array, value, start, end)
filter(collection, predicate)
find(collection, fromIndex)
findIndex(array, predicate, fromIndex)
findKey(object, predicate)
findLast(collection)
findLastIndex(array, predicate, fromIndex)
findLastKey(object, predicate)
flatMap(collection, iteratee)
flatMapDeep(collection, iteratee)
flatMapDepth(collection, iteratee, depth)
flatRest(func)
flatten(array)
flattenDeep(array)
flattenDepth(array, depth)
flip(func)
floor(number, precision)
flow(funcs)
flowRight(funcs)
forEach(collection, iteratee)
forEachRight(collection, iteratee)
forIn(object, iteratee)
forInRight(object, iteratee)
forOwn(object, iteratee)
forOwnRight(object, iteratee)
fromPairs(pairs)
functions(object)
functionsIn(object)
get(object, path, defaultValue)
getAllKeys(object)
getAllKeysIn(object)
getFuncName(func)
getHolder(func)
getIteratee()
getMapData(map, key)
getMatchData(object)
getNative(object, key)
getRawTag(value)
getTag(value)
getValue(object, key)
getView(start, end, transforms)
getWrapDetails(source)
groupBy(collection)
gt(value, other)
gte(value, other)
has(object, path)
hasIn(object, path)
hasPath(object, path, hasFunc)
hasUnicode(string)
hasUnicodeWord(string)
hashClear()
hashDelete(key)
hashGet(key)
hashHas(key)
hashSet(key, value)
head(array)
identity(value)
inRange(number, start, end)
includes(collection, value, fromIndex, guard)
indexOf(array, value, fromIndex)
initCloneArray(array)
initCloneByTag(object, tag, isDeep)
initCloneObject(object)
initial(array)
insertWrapDetails(source, details)
intersection(arrays)
intersectionBy(arrays)
intersectionWith(arrays, comparator)
invert(object)
invertBy(object)
invoke(object, path, args)
invokeMap(collection, path, args)
isArguments(value)
isArray(value)
isArrayBuffer(value)
isArrayLike(value)
isArrayLikeObject(value)
isBoolean(value)
isBuffer(value)
isDate(value)
isElement(value)
isEmpty(value)
isEqual(value, other)
isEqualWith(value, other, customizer)
isError(value)
isFinite(value)
isFlattenable(value)
isFunction(value)
isIndex(value, length)
isInteger(value)
isIterateeCall(value, index, object)
isKey(value, object)
isKeyable(value)
isLaziable(func)
isLength(value)
isMap(value)
isMasked(func)
isMatch(object, source)
isMatchWith(object, source, customizer)
isNaN(value)
isNative(value)
isNil(value)
isNull(value)
isNumber(value)
isObject(value)
isObjectLike(value)
isPlainObject(value)
isPrototype(value)
isRegExp(value)
isSafeInteger(value)
isSet(value)
isStrictComparable(value)
isString(value)
isSymbol(value)
isTypedArray(value)
isUndefined(value)
isWeakMap(value)
isWeakSet(value)
iteratee(func)
iteratorToArray(iterator)
join(array, separator)
kebabCase(string)
keyBy(collection)
keys(object)
keysIn(object)
last(array)
lastIndexOf(array, value, fromIndex)
lazyClone()
lazyReverse()
lazyValue()
listCacheClear()
listCacheDelete(key)
listCacheGet(key)
listCacheHas(key)
listCacheSet(key, value)
lodash(value)
lowerCase(string)
lowerFirst(string)
lt(value, other)
lte(value, other)
map(collection, iteratee)
mapCacheClear()
mapCacheDelete(key)
mapCacheGet(key)
mapCacheHas(key)
mapCacheSet(key, value)
mapKeys(object, iteratee)
mapToArray(map)
mapValues(object, iteratee)
matches(source)
matchesProperty(path, srcValue)
matchesStrictComparable(key, srcValue)
max(array)
maxBy(array, iteratee)
mean(array)
meanBy(array, iteratee)
memoize(func, resolver)
memoizeCapped(func)
merge(object, sources)
mergeData(data, source)
mergeWith(object, sources, customizer)
method(path, args)
methodOf(object, args)
min(array)
minBy(array, iteratee)
mixin(object, source, options)
multiply(multiplier, multiplicand)
nativeKeys()
nativeKeysIn(object)
negate(predicate)
noConflict()
noop()
nth(array, n)
nthArg(n)
objectToString(value)
omit(object, paths)
omitBy(object, predicate)
once(func)
orderBy(collection, iteratees, orders, guard)
over()
overArg(func, transform)
overArgs(func)
overEvery()
overRest(func, start, transform)
overSome()
pad(string, length, chars)
padEnd(string, length, chars)
padStart(string, length, chars)
parent(object, path)
parseInt(string, radix, guard)
partial(func, partials)
partialRight(func, partials)
partition(collection)
pick(object, paths)
pickBy(object, predicate)
property(path)
propertyOf(object)
pull(array, values)
pullAll(array, values)
pullAllBy(array, values, iteratee)
pullAllWith(array, values, comparator)
pullAt(array, indexes)
random(lower, upper, floating)
range(start, end, step)
rangeRight(start, end, step)
rearg(func, indexes)
reduce(collection, iteratee, accumulator)
reduceRight(collection, iteratee, accumulator)
reject(collection, predicate)
remove(array, predicate)
reorder(array, indexes)
repeat(string, n, guard)
replace()
replaceHolders(array, placeholder)
rest(func, start)
result(object, path, defaultValue)
reverse(array)
round(number, precision)
safeGet(object, key)
sample(collection)
sampleSize(collection, n, guard)
set(object, path, value)
setCacheAdd(value)
setCacheHas(value)
setData(func, data)
setToArray(set)
setToPairs(set)
setToString(func, string)
setWith(object, path, value, customizer)
setWrapToString(wrapper, reference, bitmask)
shortOut(func)
shuffle(collection)
shuffleSelf(array, size)
size(collection)
slice(array, start, end)
snakeCase(string)
some(collection, predicate, guard)
sortBy(collection)
sortedIndex(array, value)
sortedIndexBy(array, value, iteratee)
sortedIndexOf(array, value)
sortedLastIndex(array, value)
sortedLastIndexBy(array, value, iteratee)
sortedLastIndexOf(array, value)
sortedUniq(array)
sortedUniqBy(array, iteratee)
split(string, separator, limit)
spread(func, start)
stackClear()
stackDelete(key)
stackGet(key)
stackHas(key)
stackSet(key, value)
startCase(string)
startsWith(string, target, position)
strictIndexOf(array, value, fromIndex)
strictLastIndexOf(array, value, fromIndex)
stringSize(string)
stringToArray(string)
stringToPath(string)
stubArray()
stubFalse()
stubObject()
stubString()
stubTrue()
subtract(minuend, subtrahend)
sum(array)
sumBy(array, iteratee)
tail(array)
take(array, n, guard)
takeRight(array, n, guard)
takeRightWhile(array, predicate)
takeWhile(array, predicate)
tap(value, interceptor)
template(string, options, guard)
throttle(func, wait, options)
thru(value, interceptor)
times(n, iteratee)
toArray(value)
toFinite(value)
toInteger(value)
toKey(value)
toLength(value)
toLower(value)
toNumber(value)
toPairs(object)
toPairsIn(object)
toPath(value)
toPlainObject(value)
toSafeInteger(value)
toSource(func)
toString(value)
toUpper(value)
transform(object, iteratee, accumulator)
trim(string, chars, guard)
trimEnd(string, chars, guard)
trimStart(string, chars, guard)
truncate(string, options)
unary(func)
unescape(string)
unicodeSize(string)
unicodeToArray(string)
unicodeWords(string)
union(arrays)
unionBy(arrays)
unionWith(arrays, comparator)
uniq(array)
uniqBy(array, iteratee)
uniqWith(array, comparator)
uniqueId(prefix)
unset(object, path)
unzip(array)
unzipWith(array, iteratee)
update(object, path, updater)
updateWith(object, path, updater, customizer)
updateWrapDetails(details, bitmask)
upperCase(string)
upperFirst(string)
values(object)
valuesIn(object)
without(array, values)
words(string, pattern, guard)
wrap(value, wrapper)
wrapperAt(paths)
wrapperChain()
wrapperClone(wrapper)
wrapperCommit()
wrapperNext()
wrapperPlant(value)
wrapperReverse()
wrapperToIterator()
wrapperValue()
xor(arrays)
xorBy(arrays)
xorWith(arrays, comparator)
zip(arrays)
zipObject(props, values)
zipObjectDeep(props, values)
zipWith(arrays)
```

=== STUB ===
```javascript
function equalArrays(array, other, bitmask, customizer, equalFunc, stack) {
    // TODO: implement according to the specification
}
```
