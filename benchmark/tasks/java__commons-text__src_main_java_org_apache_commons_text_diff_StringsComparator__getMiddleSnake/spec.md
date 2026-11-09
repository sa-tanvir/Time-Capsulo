# Functional specification

## 1. Component overview

`StringsComparator.getMiddleSnake(start1, end1, start2, end2)` locates the "middle snake" of a shortest edit path between the sub-sequences `left[start1, end1)` and `right[start2, end2)`, following Eugene Myers' linear-space divide-and-conquer diff algorithm (the O(ND) paper, section 4b). The caller uses the snake to split the problem in two halves.

## 2. Functional requirements

Let `m = end1 - start1`, `n = end2 - start2`, `delta = m - n`, `sum = m + n`, `offset = (sum rounded up to the next even number) / 2`. Positions on diagonals are stored in the two arrays `vDown` (forward search) and `vUp` (reverse search). **Index convention (important, the two arrays are indexed differently):** for a diagonal number `k` (relative to the sub-ranges), the forward x of diagonal `k` lives at `vDown[k + offset]`, and the reverse x of the same diagonal `k` lives at `vUp[k + offset - delta]`. Consequently the reverse x belonging to the diagonal at `vDown[j]` is `vUp[j - delta]`, and the forward x belonging to the diagonal at `vUp[i]` is `vDown[i + delta]`. Neighbouring diagonals `k-1`, `k+1` are the neighbouring array cells (index -1, +1) in the same array.

1. If `m == 0` or `n == 0`, return `null`.
2. Otherwise run a bidirectional search for `d = 0, 1, 2, ..., offset`. Seed: `vDown[1 + offset] = start1` and `vUp[1 + offset] = end1 + 1`.
3. For each `d`, first do the **forward pass** for `k = -d, -d+2, ..., d` (in increasing order), with `i = k + offset`. Take the value of the cell above (`i+1`) when `k` is the first diagonal of the pass (`-d`), or when `k` is not the last diagonal of the pass and the cell below (`i-1`) holds a strictly smaller value than the cell above; store it in `vDown[i]`. In every other case store the cell below (`i-1`) plus one. Then let `x = vDown[i]`, `y = (x - start1) + (start2 - k)`, and repeat as long as `x` is below `end1`, `y` is below `end2` and the character of `left` at `x` equals the character of `right` at `y`: increment both and store the new `x` into `vDown[i]` each time. Then, **only if `delta` is odd** and `delta - d <= k <= delta + d`: if the reverse x of this diagonal, `vUp[i - delta]`, is not beyond (is at most) the forward x `vDown[i]`, equality included, the paths overlap: return the snake that starts at `vUp[i - delta]` on diagonal `k + start1 - start2`, extended using `end1` and `end2` (see context: the helper that takes the start x, the diagonal, `end1`, `end2`).
4. Then do the **reverse pass** for `k = delta - d, delta - d + 2, ..., delta + d` (increasing), with `i = k + offset - delta` (index into `vUp`). When `k` is the first diagonal of the pass (`delta - d`), or when `k` is not the last one (`delta + d`) and the cell above (`i+1`) holds a value less than or equal to the cell below (`i-1`), store in `vUp[i]` the value of the cell above minus one. In every other case store the value of the cell below (`i-1`) unchanged. Then let `x = vUp[i] - 1`, `y = (x - start1) + (start2 - k)`, and repeat as long as `x` is at least `start1`, `y` is at least `start2` and the character of `left` at `x` equals the character of `right` at `y`: store `x` into `vUp[i]`, then decrement both. Then, **only if `delta` is even** and `-d <= k <= d`: if the reverse x `vUp[i]` is less than or equal to the forward x of the same diagonal (stored at `vDown[k + offset]`, which is `vDown[i + delta]`; equality counts as overlap) the paths overlap: return the snake that starts at `vUp[i]` (the reverse x just computed, NOT a different cell of `vUp`) on diagonal `k + start1 - start2`, extended using `end1` and `end2`.
5. If the loop ends without an overlap, throw `RuntimeException` with the message `Internal Error` (this cannot happen for valid ranges).

The first overlap found in this order (increasing `d`, forward pass before reverse pass, diagonals in the stated order) determines the result; ties must be resolved exactly as described.

## 3. Input specification

`0 <= start1 <= end1 <= left.length()` and `0 <= start2 <= end2 <= right.length()`. The ranges may be empty, which yields `null`.

## 4. Output specification

A `Snake(start, end, diag)` or `null`. `start`/`end` are indices into `left`; `diag = x - y` of the snake's diagonal. The snake may be empty (`start == end`). Example: for `left = "abc"` and `right = ""` (full ranges) the result is `null`; for identical non-empty strings the returned snake lies on diagonal 0.

## 5. Edge cases and constraints

- The scratch arrays `vDown` and `vUp` are overwritten; their content before the call is irrelevant, and no other state changes. The sequences are never modified.
- Single call is not thread-safe on the same instance because of the shared scratch arrays.
