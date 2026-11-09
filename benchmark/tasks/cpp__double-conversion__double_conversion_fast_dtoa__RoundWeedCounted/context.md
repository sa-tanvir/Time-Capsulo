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
// in DigitGenCounted() (precision mode: a fixed number of digits is requested):
//   rest      = remaining part below the last generated digit, rest < ten_kappa
//   unit      = the accumulated error of the input number
return RoundWeedCounted(buffer, *length, rest, static_cast<uint64_t>(divisor) << -one.e(), w_error, kappa);
// and for the fractional digits:
return RoundWeedCounted(buffer, *length, fractionals, one.f(), w_error, kappa);
```

Related function in the same file (not needed): `RoundWeed`.
