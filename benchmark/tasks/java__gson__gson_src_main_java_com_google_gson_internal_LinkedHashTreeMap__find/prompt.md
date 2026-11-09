You are an expert Java developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Java code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```java code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `gson/src/main/java/com/google/gson/internal/LinkedHashTreeMap.java`
- **Enclosing scope:** `public final class LinkedHashTreeMap<K, V> extends AbstractMap<K, V> implements Serializable`

## Imports / includes available in this file

```
import java.io.ObjectStreamException;
import java.io.Serializable;
import java.util.AbstractMap;
import java.util.AbstractSet;
import java.util.Arrays;
import java.util.Comparator;
import java.util.ConcurrentModificationException;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.NoSuchElementException;
import java.util.Set;
```

## Other functions defined in the same file (signatures only; you may call them)

```
LinkedHashTreeMap::AvlBuilder::add( Node<K,V> node)
LinkedHashTreeMap::AvlBuilder::reset( int targetSize)
LinkedHashTreeMap::AvlBuilder::root()
LinkedHashTreeMap::AvlIterator::next()
LinkedHashTreeMap::AvlIterator::reset( Node<K,V> root)
LinkedHashTreeMap::Comparator<Comparable>()
LinkedHashTreeMap::EntrySet::clear()
LinkedHashTreeMap::EntrySet::contains( Object o)
LinkedHashTreeMap::EntrySet::iterator()
LinkedHashTreeMap::EntrySet::remove( Object o)
LinkedHashTreeMap::EntrySet::size()
LinkedHashTreeMap::KeySet::clear()
LinkedHashTreeMap::KeySet::contains( Object o)
LinkedHashTreeMap::KeySet::iterator()
LinkedHashTreeMap::KeySet::remove( Object key)
LinkedHashTreeMap::KeySet::size()
LinkedHashTreeMap::LinkedHashTreeMap( Comparator<?super K> comparator)
LinkedHashTreeMap::LinkedHashTreeMap()
LinkedHashTreeMap::LinkedTreeMapIterator::LinkedTreeMapIterator()
LinkedHashTreeMap::LinkedTreeMapIterator::hasNext()
LinkedHashTreeMap::LinkedTreeMapIterator::nextNode()
LinkedHashTreeMap::LinkedTreeMapIterator::remove()
LinkedHashTreeMap::Node::Node( Node<K,V> parent , K key , int hash , Node<K,V> next , Node<K,V> prev)
LinkedHashTreeMap::Node::Node()
LinkedHashTreeMap::Node::equals( Object o)
LinkedHashTreeMap::Node::first()
LinkedHashTreeMap::Node::getKey()
LinkedHashTreeMap::Node::getValue()
LinkedHashTreeMap::Node::hashCode()
LinkedHashTreeMap::Node::last()
LinkedHashTreeMap::Node::setValue( V value)
LinkedHashTreeMap::Node::toString()
LinkedHashTreeMap::clear()
LinkedHashTreeMap::containsKey( Object key)
LinkedHashTreeMap::doubleCapacity( Node<K,V> [ ] oldTable)
LinkedHashTreeMap::doubleCapacity()
LinkedHashTreeMap::entrySet()
LinkedHashTreeMap::equal( Object a , Object b)
LinkedHashTreeMap::findByEntry( Entry<?,?> entry)
LinkedHashTreeMap::findByObject( Object key)
LinkedHashTreeMap::get( Object key)
LinkedHashTreeMap::keySet()
LinkedHashTreeMap::put( K key , V value)
LinkedHashTreeMap::rebalance( Node<K,V> unbalanced , boolean insert)
LinkedHashTreeMap::remove( Object key)
LinkedHashTreeMap::removeInternal( Node<K,V> node , boolean unlink)
LinkedHashTreeMap::removeInternalByKey( Object key)
LinkedHashTreeMap::replaceInParent( Node<K,V> node , Node<K,V> replacement)
LinkedHashTreeMap::rotateLeft( Node<K,V> root)
LinkedHashTreeMap::rotateRight( Node<K,V> root)
LinkedHashTreeMap::secondaryHash( int h)
LinkedHashTreeMap::size()
LinkedHashTreeMap::writeReplace()
```

## Instance state

Fields of `LinkedHashTreeMap<K,V>` used by the method:

- `comparator` (`Comparator<? super K>`, package-private): defines the order of keys inside one bucket; never null. When the map was created without a comparator it is the shared constant `NATURAL_ORDER`.
- `NATURAL_ORDER` (`private static final Comparator<Comparable>`): the natural-order comparator (`a.compareTo(b)`); recognised by identity (`comparator == NATURAL_ORDER`).
- `table` (`Node<K,V>[]`, package-private): the hash table, length a power of two (initially 16). `table[i]` is the root of an AVL tree holding all keys whose scrambled hash `h` satisfies `h & (table.length - 1) == i`, or `null` if the bucket is empty.
- `size` (`int`) and `modCount` (`int`): number of entries and structural modification counter (both package-private).
- `threshold` (`int`, package-private): table capacity (`table.length`) times 3/4; when the table is enlarged, `threshold` is recomputed by the private `doubleCapacity()`.
- `header` (`final Node<K,V>`): sentinel of the circular linked list that defines iteration order; `header.prev` is the most recently inserted node.
- `secondaryHash(int h)` (`private static int`): scrambles a `hashCode()` value; use it for every key hash.
- `doubleCapacity()` (private, no arguments): doubles `table.length`, re-splitting every bucket tree, and recomputes `threshold`.

`Node<K,V>` (package-private `static final class` nested in the map, implements `Map.Entry`) fields, all package-private:

- `parent`, `left`, `right` (`Node<K,V>`): links of the AVL tree; `null` when absent. The root of a tree has `parent == null`.
- `next`, `prev` (`Node<K,V>`): links of the circular doubly linked list (through `header`) that defines iteration order (insertion order).
- `key` (`K`, final), `value` (`V`), `height` (`int`): the height of the subtree rooted at this node; a leaf has height 1, a missing (`null`) child counts as height 0.
- `hash` (`int`, final): the scrambled hash of the key (the value returned by `secondaryHash(key.hashCode())`), stored when the node is created.

Sibling members you may use: `Node.first()` / `Node.last()` return the leftmost / rightmost node of a subtree; `rotateLeft(Node root)` / `rotateRight(Node root)` (private) rotate the subtree rooted at `root` so that its right (left) child becomes the subtree root, fixing parent links (the new subtree root takes over `root`'s place in its parent, or becomes the tree root) and the heights of the two nodes involved; `replaceInParent(node, replacement)` (private) puts `replacement` where `node` was.

`Node` constructor: `Node(Node<K,V> parent, K key, int hash, Node<K,V> next, Node<K,V> prev)` creates a leaf (height 1) with the given parent and key, and links it into the iteration list between `prev` and `next` (so `new Node(parent, key, ..., header, header.prev)` appends it at the end of the iteration order). Sibling methods you may call: `rebalance(Node<K,V> unbalanced, boolean insert)` (private).

=== STUB ===
```java
Node<K, V> find(K key, boolean create) {
    // TODO: implement according to the specification
}
```
