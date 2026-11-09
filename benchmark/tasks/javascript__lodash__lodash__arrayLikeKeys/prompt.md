You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `arrayLikeKeys(value, inherited)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14. It produces the list of enumerable string
property names of an *array-like* value. `_.keys(value)` calls it as
`arrayLikeKeys(value)` and `_.keysIn(value)` as `arrayLikeKeys(value, true)`
whenever `isArrayLike(value)` is true (arrays, `arguments` objects, strings and
`String` objects, typed arrays, buffers, plain objects with a valid numeric
`length`, ...). Through `keys`/`keysIn` it is used by `_.forOwn`, `_.forIn`,
`_.findKey`, `_.mapValues`, `_.assign`, `_.clone`, `_.merge`, `_.toPairs`,
`_.values`, `_.isEqual` and many more. The function differs from a plain
`for..in` collection in that the index keys of genuine indexed collections are
always reported, in ascending order, even when the collection is sparse.

## 2. Functional requirements

1. Classify `value` as an *indexed collection* when it is any of: an array
   (`isArray`), an `arguments` object (`isArguments`), a Node.js `Buffer`
   (`isBuffer`), or a typed array (`isTypedArray`). Everything else (string
   primitives, `String` objects, plain array-like objects such as
   `{ '0': 'a', length: 1 }`, functions are never passed) is *not* an indexed
   collection.
2. For an indexed collection of length `n`, the result starts with the strings
   `'0'`, `'1'`, ..., `String(n - 1)` in ascending order, for **every** index
   below `n`, whether or not the element exists (holes in sparse arrays are
   reported as if present: `[1, , 3]` gives `['0', '1', '2']`).
3. Afterwards, append every key produced by enumerating `value` with a
   `for..in` loop (which yields own and inherited enumerable string keys, in the
   engine's enumeration order), keeping a key only if:
   - when `inherited` is falsy, the key is an **own** property of `value`
     (checked with `Object.prototype.hasOwnProperty`); when `inherited` is
     truthy, inherited enumerable keys are kept too;
   - and, only for indexed collections, the key is not one that would duplicate
     or pollute the index list: it is not `'length'`; for buffers it is not
     `'offset'` or `'parent'`; for typed arrays it is not `'buffer'`,
     `'byteLength'` or `'byteOffset'`; and it is not a valid index below `n`
     (a canonical non-negative integer string such as `'0'` or `'17'` whose
     numeric value is less than `n`).
   Keys that look numeric but are not valid indices below `n` (e.g. `'-1'`,
   `'1.5'`, `'01'`, or `'7'` on an `arguments` object of length 3) are
   ordinary keys and are kept, in enumeration order.
4. For values that are not indexed collections, no index list is generated and
   no key is filtered other than by the own/inherited rule; the result is just
   the filtered `for..in` sequence. For a string primitive or `String` object,
   this yields its character indices (`'0'`, `'1'`, ...) followed by any extra
   own (or inherited, if requested) enumerable keys. For `{ '0': 'a', length: 1 }`
   it yields `['0', 'length']`.
5. Return a new array of strings. `value` is never modified.

## 3. Input specification

- `value`: an array-like value (never `null`/`undefined`): array (possibly
  sparse or with extra non-index properties), `arguments` object (strict or
  sloppy), `Buffer`, any typed array (`Int8Array` ... `Float64Array`,
  `Uint8ClampedArray`), string primitive, `String` object, or an object whose
  `length` is an integer in `[0, Number.MAX_SAFE_INTEGER]`.
- `inherited`: optional; truthy to also include inherited enumerable string keys
  (as `_.keysIn` does), falsy/absent for own keys only (as `_.keys` does).

## 4. Output specification

A new array of property-name strings, index keys (for indexed collections) first
in ascending order, then the remaining keys in `for..in` order.

Examples (`f` = `arrayLikeKeys`):

- `f([1, 2, 3])` -> `['0', '1', '2']`
- sparse `var a = [1]; a[2] = 3;` -> `f(a)` is `['0', '1', '2']`
- `var a = [1]; a.a = 1;` -> `['0', 'a']`
- with `Array.prototype.a = 1` set: `f([1])` -> `['0']`, `f([1], true)` -> `['0', 'a']`
- `arguments` object of `(1, 2, 3)` with an extra own property `a` -> `['0', '1', '2', 'a']`
  (strict-mode `arguments` objects behave the same; their `length` is never reported)
- with `Object.prototype.a = 1`: `f(argumentsOf123)` -> `['0','1','2']`,
  `f(argumentsOf123, true)` -> `['0','1','2','a']`
- `f(Object('abc'))` -> `['0', '1', '2']`; `f('abc')` -> `['0', '1', '2']`
- `var s = Object('a'); s.a = 1;` -> `['0', 'a']`; with `String.prototype.a = 1`,
  `f(Object('a'))` -> `['0']` and `f(Object('a'), true)` -> `['0', 'a']`
- `f({ '0': 'a', length: 1 })` -> `['0', 'length']`
- `f(new Uint8Array(2))` -> `['0', '1']`; `f(Buffer.from('ab'))` -> `['0', '1']`
- `f([])` -> `[]`; `f('')` -> `[]`

## 5. Edge cases and constraints

- Holes in arrays and `arguments` objects are reported; the index list depends
  only on `length`, not on which elements exist.
- An own enumerable `length` property (some engines expose one on strict
  `arguments`) must never appear for indexed collections, but must appear for
  plain array-like objects.
- The function must not mutate `value` and must not invoke anything on it other
  than reading `length`, enumerating it, and own-property checks.
- The result is always a fresh array; ordering is significant and must be as
  described (callers such as `_.findKey` and `_.forOwn` depend on it).
- Performance: linear in `length` plus the number of enumerable keys.

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

- `baseTimes(n, iteratee)`: The base implementation of `_.times` without support for iteratee shorthands or max array length checks.
- `isIndex(value, length)`: Checks if `value` is a valid array-like index.
- `isArguments(value)`: Checks if `value` is likely an `arguments` object.
- `isArray(value)`: Checks if `value` is classified as an `Array` object.
- `isBuffer(value)`: Checks if `value` is a buffer.
- `isTypedArray(value)`: Checks if `value` is classified as a typed array.

Values (declarations as in lodash.js):

```
var hasOwnProperty = objectProto.hasOwnProperty;
```

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
equalArrays(array, other, bitmask, customizer, equalFunc, stack)
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
function arrayLikeKeys(value, inherited) {
    // TODO: implement according to the specification
}
```
