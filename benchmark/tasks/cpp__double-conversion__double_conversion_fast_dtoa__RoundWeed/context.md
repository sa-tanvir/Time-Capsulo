# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/fast-dtoa.cc` (namespace `double_conversion`)
- **Target:** a file-local (`static`) function. Keep the signature exactly as in the stub.

## Includes available in this file

```
#include "fast-dtoa.h"
#include "cached-powers.h"
#include "diy-fp.h"
#include "ieee.h"
```
(`utils.h` comes with them: `Vector<T>`, `ASSERT`, `uint64_t`, ...)

## Types available

```
template <typename T> class Vector {            // simplified view over caller-owned memory
 public:
  Vector(T* data, int len);
  int length() const;
  T* start() const;
  T& operator[](int index) const;               // buffer[i] is a reference to the i-th element (assignable)
};
```

The digits in `buffer` are ASCII characters (`'0'` .. `'9'`); they are modified in place through `buffer[i]`.

## Callers (for orientation only)

```
// in DigitGen() (shortest mode), after generating the digits of too_high = high + 1 unit that lie in the unsafe interval:
//   rest      = remaining part of the value below the last generated digit (so rest < ten_kappa)
//   ten_kappa = value of one unit of the last generated digit (10^kappa scaled to the fixed-point unit)
return RoundWeed(buffer, *length, DiyFp::Minus(too_high, w).f(), unsafe_interval.f(), rest, ten_kappa, unit);
// (also called with  DiyFp::Minus(too_high, w).f() * unit  and  ten_kappa = static_cast<uint64_t>(1) << -one.e()  for the fractional digits)
```

Related function in the same file (not needed): `RoundWeedCounted`.
