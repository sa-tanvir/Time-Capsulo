# Context for the function to implement

- **Language:** python
- **File:** `more_itertools/recipes.py`

## Imports / includes available in this file

```
import warnings
from collections import deque
from itertools import (
    chain,
    combinations,
    count,
    cycle,
    filterfalse,
    groupby,
    islice,
    repeat,
    starmap,
    tee,
    zip_longest,
)
import operator
from random import randrange, sample, choice
```

## Other functions defined in the same file (signatures only; you may call them)

```
all_equal( iterable )
consume( iterator , n = None )
dotproduct( vec1 , vec2 )
first_true( iterable , default = None , pred = None )
flatten( listOfLists )
grouper( iterable , n , fillvalue = None )
iter_except( func , exception , first = None )
ncycles( iterable , n )
nth( iterable , n , default = None )
nth_combination( iterable , r , index )
padnone( iterable )
pairwise( iterable )
partition( pred , iterable )
powerset( iterable )
prepend( value , iterator )
quantify( iterable , pred = bool )
random_combination( iterable , r )
random_combination_with_replacement( iterable , r )
random_permutation( iterable , r = None )
random_product( * args , ** kwds )
repeatfunc( func , times = None , * args )
roundrobin( * iterables )
tabulate( function , start = 0 )
tail( n , iterable )
take( n , iterable )
unique_justseen( iterable , key = None )
```
