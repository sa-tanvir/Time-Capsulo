# Context for the function to implement

- **Language:** javascript
- **File:** `lib/utils.js`

## Imports / includes available in this file

```
(none)
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( $0 )
(anonymous) ( )
(anonymous) ( acc , key )
(anonymous) ( item , i )
arrayToObject ( source , options )
assignSingleSource ( target , source )
combine ( a , b )
compact ( value )
compactQueue ( queue )
decode ( str , decoder , charset )
isBuffer ( obj )
isRegExp ( obj )
merge ( target , source , options )
```

## Variables declared at the same scope level (you may use them)

```
var has = Object.prototype.hasOwnProperty;
var isArray = Array.isArray;
var hexTable = (function () {
    var array = [];
    for (var i = 0; i < 256; ++i) {
        array.push('%' + ((i < 16 ? '0' : '') + i.toString(16)).toUpperCase());
    }

    return array;
}());
```
