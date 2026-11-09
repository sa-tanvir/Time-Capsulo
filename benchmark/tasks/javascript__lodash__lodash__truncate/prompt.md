You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `truncate(string, options)` in `lodash.js`

## 1. Component overview

Public lodash 4.17.14 method `_.truncate([string=''], [options={}])`. It shortens
`string` if it is longer than a maximum length. The last characters of the
shortened string are replaced with an *omission* string (default `'...'`), and
the cut can be moved back to the last occurrence of a *separator*. Lengths are
measured in user-visible symbols when the string contains Unicode symbols that
span several UTF-16 code units (astral characters, combining marks, emoji
sequences), otherwise in code units. Returns the truncated string.

## 2. Functional requirements

1. **Options.** Defaults: `length = 30`, `omission = '...'`, no separator.
   Only if `options` is an object (`isObject`: objects, arrays, functions) are
   options read; any other `options` (e.g. the index number passed by `_.map`)
   is ignored, so `_.map([s, s], _.truncate)` truncates each with defaults.
   Each option is read only if present according to the `in` operator
   (own or inherited):
   - `length`: converted with `toInteger` (`'4'` -> 4, `4.6` -> 4, `''` / `NaN` -> 0;
     objects are coerced through `valueOf`).
   - `omission`: converted to a string with `baseToString`, so an explicitly
     present `null` becomes `'null'` and `undefined` becomes `'undefined'`.
   - `separator`: a `RegExp` or a string (any other value is used via its string
     form). Present-but-`undefined` means "no separator".
2. `string` is converted with `toString` (`null`/`undefined` -> `''`; objects via
   their `toString`, `String` objects to their primitive value).
3. Let the *size* of the string be its number of symbols if it contains Unicode
   symbols (`hasUnicode`), each symbol being one element of `stringToArray`;
   otherwise its `length` in code units.
4. If `length >= size`, return the converted string unchanged.
5. Otherwise let `end = length - stringSize(omission)` (omission measured in
   symbols). If `end < 1` return just the omission (so a `length` of 0 or a
   negative length returns `'...'` with default omission).
6. Take the first `end` symbols (Unicode case) or code units of the string as the
   kept prefix.
7. Without a separator, return `prefix + omission`.
8. With a separator, let `cut` be the position in the original string (in code
   units) right after the kept prefix.
   - **RegExp separator:** if the remainder of the string starting at `cut` does
     *not* begin with a match of the separator (no match at all, or first match
     at a position > 0), find the **last** match of the separator inside the
     prefix, scanning matches left to right from the start of the prefix (as a
     global search does); if one exists, shorten the prefix to end just before
     that match. Non-global regexes must behave like their global version with
     the same source and flags (e.g. `/,? +/` and `/,? +/g` give the same
     result). A caller's global regex may have its `lastIndex` reset/used, but
     the result must not depend on its initial `lastIndex`.
   - **String separator:** if the original string does not contain the separator
     exactly at position `cut`, shorten the prefix to end just before the
     separator's last occurrence in the prefix, if it occurs there.
   - If the remainder begins with the separator, the prefix is kept as is.
   Return `prefix + omission`.

## 3. Input specification

- `string`: usually a string; any value is accepted and coerced as above.
- `options`: optional; object with optional `length` (number-like), `omission`
  (any, stringified), `separator` (RegExp or string); non-objects are ignored.

## 4. Output specification

A string primitive. Examples with `s = 'hi-diddly-ho there, neighborino'`
(31 code units):

- `truncate(s)` -> `'hi-diddly-ho there, neighbo...'`
- `truncate(s, { length: 31 })` and `{ length: 33 }` -> `s` unchanged
- `truncate(s, { length: 24 })` -> `'hi-diddly-ho there, n...'`
- `truncate(s, { omission: ' [...]' })` -> `'hi-diddly-ho there, neig [...]'`
- `truncate(s, { omission: null })` -> `'hi-diddly-ho there, neighbnull'`
- `truncate(s, { omission: undefined })` -> `'hi-diddly-ho there, nundefined'`
- `truncate(s, { length: 4 })` -> `'h...'`
- `truncate(s, { length: 24, separator: ' ' })` -> `'hi-diddly-ho there,...'`
- `truncate(s, { length: 24, separator: /,? +/ })` -> `'hi-diddly-ho there...'`
  (same with `/,? +/g`)
- `truncate(s, { length: 0 })`, `{ length: -2 }` -> `'...'`
- `truncate(s, { length: { valueOf: () => 4.6 } })` -> `'h...'`;
  with `valueOf` returning `'4'` -> `'h...'`; returning `''` or `NaN` -> `'...'`
- `truncate(Object(s), { length: 4 })` -> `'h...'`;
  `truncate({ toString: () => s }, { length: 5 })` -> `'hi...'`
- `truncate(null)`, `truncate(undefined)`, `truncate('')` -> `''`
- Unicode: with leaf `'🍂'` and a ZWJ family emoji `G`,
  `t = 'A ' + leaf + ', ' + G + ', and 🚀'` has 13 symbols:
  `truncate(t, { length: 13 })` -> `t`; `truncate(t, { length: 6 })` ->
  `'A ' + leaf + '...'`. With `h = '💕'` and `{ length: 4, separator: h }`
  (or `RegExp(h)`): `truncate(t, ...)` -> `'A...'`; for `h` repeated 10 times
  the result is `h + '...'` (length 5 code units), because the remainder after
  the prefix begins with the separator.

## 5. Edge cases and constraints

- Never mutates `options` (other than a global separator regex's `lastIndex`) or
  the input.
- Astral characters and grapheme sequences must never be split in the Unicode case.
- `omission` may itself be longer than `length`; then only the omission is
  returned.
- Zero-length regex matches: a RegExp separator that can match the empty
  string (e.g. `/x*/`, `/\b/`, `/(?=,)/`) is supported only when the
  remainder search of rule 8 finds a match at position 0 (then the prefix is
  kept, as for `/x*/`, which always matches empty at 0). If such a separator
  matches the remainder only later and can match empty inside the prefix, the
  behaviour is outside the contract (the original never terminates). Callers
  and tests never do this.
- Linear time in the length of the input string.

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

- `baseToString(value)`: The base implementation of `_.toString` which doesn't convert nullish values to empty strings.
- `castSlice(array, start, end)`: Casts `array` to a slice if it's needed.
- `hasUnicode(string)`: Checks if `string` contains Unicode symbols.
- `isObject(value)`: Checks if `value` is the [language type](http://www.ecma-international.org/ecma-262/7.0/#sec-ecmascript-language-types) of `Object`. (e.g. arrays, functions, objects, regexes, `new Number(0)`, and `new String('')`)
- `stringSize(string)`: Gets the number of symbols in `string`.
- `stringToArray(string)`: Converts `string` to an array.
- `toInteger(value)`: Converts `value` to an integer.
- `toString(value)`: Converts `value` to a string. An empty string is returned for `null` and `undefined` values. The sign of `-0` is preserved.
- `isRegExp(value)`: Checks if `value` is classified as a `RegExp` object.

Values (declarations as in lodash.js):

```
var DEFAULT_TRUNC_LENGTH = 30;
var DEFAULT_TRUNC_OMISSION = '...';
var reFlags = /\w*$/;
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
function truncate(string, options) {
    // TODO: implement according to the specification
}
```
