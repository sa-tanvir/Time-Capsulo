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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java`
- **Enclosing scope:** `public final class LinkedTreeMap<K, V> extends AbstractMap<K, V> implements Serializable`

## Imports / includes available in this file

```
import java.io.ObjectStreamException;
import java.io.Serializable;
import java.util.AbstractMap;
import java.util.AbstractSet;
import java.util.Comparator;
import java.util.ConcurrentModificationException;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.NoSuchElementException;
import java.util.Set;
```

## Other functions defined in the same file (signatures only; you may call them)

```
LinkedTreeMap::Comparator<Comparable>()
LinkedTreeMap::EntrySet::clear()
LinkedTreeMap::EntrySet::contains( Object o)
LinkedTreeMap::EntrySet::iterator()
LinkedTreeMap::EntrySet::remove( Object o)
LinkedTreeMap::EntrySet::size()
LinkedTreeMap::KeySet::clear()
LinkedTreeMap::KeySet::contains( Object o)
LinkedTreeMap::KeySet::iterator()
LinkedTreeMap::KeySet::remove( Object key)
LinkedTreeMap::KeySet::size()
LinkedTreeMap::LinkedTreeMap( Comparator<?super K> comparator)
LinkedTreeMap::LinkedTreeMap()
LinkedTreeMap::LinkedTreeMapIterator::LinkedTreeMapIterator()
LinkedTreeMap::LinkedTreeMapIterator::hasNext()
LinkedTreeMap::LinkedTreeMapIterator::nextNode()
LinkedTreeMap::LinkedTreeMapIterator::remove()
LinkedTreeMap::Node::Node( Node<K,V> parent , K key , Node<K,V> next , Node<K,V> prev)
LinkedTreeMap::Node::Node()
LinkedTreeMap::Node::equals( Object o)
LinkedTreeMap::Node::first()
LinkedTreeMap::Node::getKey()
LinkedTreeMap::Node::getValue()
LinkedTreeMap::Node::hashCode()
LinkedTreeMap::Node::last()
LinkedTreeMap::Node::setValue( V value)
LinkedTreeMap::Node::toString()
LinkedTreeMap::clear()
LinkedTreeMap::containsKey( Object key)
LinkedTreeMap::entrySet()
LinkedTreeMap::equal( Object a , Object b)
LinkedTreeMap::findByEntry( Entry<?,?> entry)
LinkedTreeMap::findByObject( Object key)
LinkedTreeMap::get( Object key)
LinkedTreeMap::keySet()
LinkedTreeMap::put( K key , V value)
LinkedTreeMap::rebalance( Node<K,V> unbalanced , boolean insert)
LinkedTreeMap::remove( Object key)
LinkedTreeMap::removeInternal( Node<K,V> node , boolean unlink)
LinkedTreeMap::removeInternalByKey( Object key)
LinkedTreeMap::replaceInParent( Node<K,V> node , Node<K,V> replacement)
LinkedTreeMap::rotateLeft( Node<K,V> root)
LinkedTreeMap::rotateRight( Node<K,V> root)
LinkedTreeMap::size()
LinkedTreeMap::writeReplace()
```

## Instance state

Fields of `LinkedTreeMap<K,V>` used by the method:

- `comparator` (`Comparator<? super K>`, package-private): defines the key order; never null. When the map was created without a comparator it is the shared constant `NATURAL_ORDER`.
- `NATURAL_ORDER` (`private static final Comparator<Comparable>`): the natural-order comparator (`a.compareTo(b)`); recognised by identity (`comparator == NATURAL_ORDER`).
- `root` (`Node<K,V>`, package-private): root of the AVL tree, `null` when the map is empty.
- `size` (`int`) and `modCount` (`int`): number of entries and structural modification counter (both package-private).
- `header` (`final Node<K,V>`): sentinel of the circular linked list that defines iteration order; `header.prev` is the most recently inserted node.

`Node<K,V>` (package-private `static final class` nested in the map, implements `Map.Entry`) fields, all package-private:

- `parent`, `left`, `right` (`Node<K,V>`): links of the AVL tree; `null` when absent. The root of a tree has `parent == null`.
- `next`, `prev` (`Node<K,V>`): links of the circular doubly linked list (through `header`) that defines iteration order (insertion order).
- `key` (`K`, final), `value` (`V`), `height` (`int`): the height of the subtree rooted at this node; a leaf has height 1, a missing (`null`) child counts as height 0.

Sibling members you may use: `Node.first()` / `Node.last()` return the leftmost / rightmost node of a subtree; `rotateLeft(Node root)` / `rotateRight(Node root)` (private) rotate the subtree rooted at `root` so that its right (left) child becomes the subtree root, fixing parent links (the new subtree root takes over `root`'s place in its parent, or becomes the tree root) and the heights of the two nodes involved; `replaceInParent(node, replacement)` (private) puts `replacement` where `node` was.

`Node` constructor: `Node(Node<K,V> parent, K key, Node<K,V> next, Node<K,V> prev)` creates a leaf (height 1) with the given parent and key, and links it into the iteration list between `prev` and `next` (so `new Node(parent, key, ..., header, header.prev)` appends it at the end of the iteration order). Sibling methods you may call: `rebalance(Node<K,V> unbalanced, boolean insert)` (private).

=== STUB ===
```java
Node<K, V> find(K key, boolean create) {
    // TODO: implement according to the specification
}
```
