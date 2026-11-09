# Functional specification

## 1. Component overview

`LinkedHashTreeMap.find(key, create)` is the lookup/insert primitive of the map: it computes the key's bucket in the hash table, locates the node holding `key` in that bucket's AVL tree, and optionally creates it (rebalancing, and growing the table when it gets full) when it is absent. `get`, `containsKey`, `put` and `remove` are built on it.

## 2. Functional requirements

1. **Bucket.** Compute `hash = secondaryHash(key.hashCode())` and the bucket index `hash & (table.length - 1)`; the tree rooted at `table[index]` (possibly empty) is the one to search.
2. **Search.** If that bucket is not empty, descend from its root, comparing `key` with each visited node's key using the map's order: for the natural-order comparator (`comparator == NATURAL_ORDER`) use `((Comparable) key).compareTo(nodeKey)`; otherwise `comparator.compare(key, nodeKey)`. A comparison of 0 means the node is found: return it (no change to the map even when `create` is true). A negative result continues into the left subtree, a positive one into the right subtree; stop when the chosen child is missing; remember the last visited node and the sign of the last comparison.
3. **Not found, `create == false`:** return `null`; the map is unchanged.
4. **Not found, `create == true`:** create a new node for `key` with the stored `hash`, and add it:
   - If the bucket is empty: when the comparator is the natural-order one and `key` is not an instance of `Comparable`, throw `ClassCastException` with message `<key.getClass().getName()> is not Comparable` (no node is added). Otherwise the new node (no parent) becomes `table[index]`.
   - If the bucket is not empty: the new node becomes the left child of the last visited node if the last comparison was negative, otherwise its right child; its parent is that node. Then restore the AVL balance by calling `rebalance(lastVisitedNode, true)`.
   - In both cases the new node is appended at the end of the iteration order (just before `header`) and `modCount` is incremented by 1. Then, **if the value of `size` before the increment is greater than `threshold`**, call `doubleCapacity()`; `size` is incremented by 1 in the same step (i.e. the comparison uses the old size). Return the new node. Its `value` is not set (null).
5. **Errors.** With the natural-order comparator, a `key` that is not mutually comparable with the keys already in its bucket makes the search throw `ClassCastException`; the map is unchanged. A `null` key is not supported (callers never pass one).

## 3. Input specification

- `key` (`K`): non-null; its `hashCode()` may be poor (many keys may share a bucket or even a full hash), so a bucket can hold a large tree.
- `create` (`boolean`): whether to add the key when missing.
- The map may hold any number of entries.

## 4. Output specification

Returns the matching or newly created `Node`, or `null` (only when `create` is false and the key is absent). Examples with natural-order `String` keys, starting from an empty map:

- `find("b", true)` returns a new node with key `"b"`, `size` becomes 1, the node is the root with height 1, `modCount` becomes 1.
- then `find("a", true)` creates a node as left child of `"b"`; `find("a", false)` returns that node; `find("z", false)` returns `null`; `find("a", true)` again returns the existing node and changes nothing.
- inserting `"a"`, `"b"`, `"c"` in that order ends with `"b"` as root of a tree of height 2 (the rebalancing is done by the helper, all keys of one bucket form one tree).
- Iteration order: nodes are appended to the iteration list in creation order.

## 5. Edge cases and constraints

- Finding an existing key never modifies the map.
- Keys with equal hash but different order live in the same bucket tree; keys with different hashes can only be compared when they land in the same bucket.
- The table grows (by `doubleCapacity()`) only as a side effect of creating a node, so after the call `table.length` may be doubled and `threshold` updated.
- Comparator exceptions propagate unchanged. Not thread-safe.
