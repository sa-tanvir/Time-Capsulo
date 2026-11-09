# Functional specification

## 1. Component overview

`LinkedTreeMap.find(key, create)` is the lookup/insert primitive of the map: it locates the node holding `key` in the AVL tree, optionally creating it (and rebalancing) when it is absent. `get`, `containsKey`, `put` and `remove` are built on it.

## 2. Functional requirements

1. **Search.** If the tree is not empty, descend from `root`, comparing `key` with each visited node's key using the map's order: for the natural-order comparator (`comparator == NATURAL_ORDER`) use `((Comparable) key).compareTo(nodeKey)`; otherwise `comparator.compare(key, nodeKey)`. A comparison of 0 means the node is found: return it (no change to the map even when `create` is true). A negative result continues into the left subtree, a positive one into the right subtree; stop when the chosen child is missing; remember the last visited node (the node at or adjacent to the key) and the sign of the last comparison.
2. **Not found, `create == false`:** return `null`; the map is unchanged.
3. **Not found, `create == true`:** create a new node for `key` and add it to the tree:
   - If the tree is empty: when the comparator is the natural-order one and `key` is not an instance of `Comparable`, throw `ClassCastException` with message `<key.getClass().getName()> is not Comparable` (no node is added). Otherwise the new node (no parent) becomes `root`.
   - If the tree is not empty: the new node becomes the left child of the last visited node if the last comparison was negative, otherwise its right child; its parent is that node. Then restore the AVL balance by calling `rebalance(lastVisitedNode, true)`.
   - In both cases the new node has height 1 before rebalancing, is appended at the end of the iteration order (just before `header`), `size` is incremented by 1 and `modCount` by 1. Return the new node. Its `value` is not set (null).
4. **Errors.** With the natural-order comparator, a `key` that is not mutually comparable with the keys already in the tree makes the search throw `ClassCastException` (for example a key that is not `Comparable` when the tree is non-empty); the map is unchanged. A `null` key is not supported (callers never pass one).

## 3. Input specification

- `key` (`K`): non-null.
- `create` (`boolean`): whether to add the key when missing.
- The map may hold any number of entries (millions); the tree must be descended in time proportional to its height.

## 4. Output specification

Returns the matching or newly created `Node`, or `null` (only when `create` is false and the key is absent). Examples with natural-order `String` keys, starting from an empty map:

- `find("b", true)` returns a new node with key `"b"`, `size` becomes 1, the node is the root with height 1, `modCount` becomes 1.
- then `find("a", true)` creates a node as left child of `"b"`; `find("a", false)` returns that node; `find("z", false)` returns `null`; `find("a", true)` again returns the existing node and changes nothing.
- inserting `"a"`, `"b"`, `"c"` in that order ends with `"b"` as root of a tree of height 2 (the rebalancing is done by the helper).
- Iteration order: nodes are appended to the iteration list in creation order.

## 5. Edge cases and constraints

- Finding an existing key never modifies the map (`size`, `modCount`, links and heights unchanged).
- A custom comparator may order keys differently from `equals`; only the comparator decides equality (compare result 0).
- Comparator exceptions propagate unchanged.
- Not thread-safe.
