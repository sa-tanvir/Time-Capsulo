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

`LinkedTreeMap.rebalance(unbalanced, insert)` restores the AVL balance of the map's binary search tree after a node was added below, or removed from below, the node `unbalanced`. It walks from `unbalanced` up to the root of the tree, correcting the stored heights and performing the AVL rotations needed so that for every node on that path the heights of its two subtrees differ by at most 1.

## 2. Functional requirements

For `node = unbalanced`, then `node.parent`, then its parent, and so on up to the tree root (stop at `null`), do the following. Let `leftHeight` / `rightHeight` be the heights of `node.left` / `node.right` (0 for a missing child), and `delta = leftHeight - rightHeight`.

- `delta == 0` or `delta == 1` or `delta == -1`: the node is balanced; set `node.height = max(leftHeight, rightHeight) + 1`.
- `delta == -2` (right-heavy): let `rightDelta = height(right.left) - height(right.right)` (missing children count 0).
  - If `rightDelta == -1`, or `rightDelta == 0` **and** `insert` is `false` (removal): rotate left at `node` (single rotation).
  - Otherwise (`rightDelta == 1`; with `insert` true a delta of 0 cannot occur): rotate right at `node.right`, then rotate left at `node` (double rotation).
- `delta == 2` (left-heavy): symmetric. Let `leftDelta = height(left.left) - height(left.right)`. If `leftDelta == 1`, or `leftDelta == 0` and `insert` is `false`: rotate right at `node`. Otherwise (`leftDelta == -1`): rotate left at `node.left`, then rotate right at `node`.
- The rotations (`rotateLeft`, `rotateRight`) fix parent links, the heights of the nodes they move, and, when the rotated node was the root of its tree, the tree's root reference (`root`).
- After a rotation (single or double), the walk continues with the new root of the rotated subtree (its height is already correct after the rotation) and then with that node's parent, and so on up to the tree root.
- Equivalent early exits are permitted but not required: when inserting, nothing above the first node whose height is unchanged or the first rotation needs any change; when removing, nothing above the first node whose height is unchanged needs any change.

After the call the whole tree must be a valid AVL tree with correct stored heights, and the shape must be exactly the one given by the rules above (the choice between single and double rotation, and the tie-break on removal, are observable through the tree shape).

## 3. Input specification

- `unbalanced`: the lowest node whose subtree height may have changed: for an insertion the parent of the newly attached node; for a removal the parent of the node that was removed (its former parent). May be `null` (nothing to do) when a root was removed.
- `insert`: `true` if the call follows an insertion, `false` if it follows a removal.
- Precondition: apart from the nodes on the path from `unbalanced` to the root, the tree is a valid AVL tree with correct heights, and every node on that path has a balance difference of at most 2 in magnitude.

## 4. Output specification

No return value; the tree is modified in place (links, heights, root reference, `root`). Example (insertion of keys 1, 2, 3 in this order into an empty map): after inserting 3 the node 1 has `delta == -2`, its right child 2 has `rightDelta == -1`, so a left rotation makes 2 the root with children 1 and 3, heights 2, 1, 1.

## 5. Edge cases and constraints

- `unbalanced == null` is a no-op.
- No exception is thrown for a valid tree.
- Runs in time proportional to the height of the tree.

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
LinkedTreeMap::find( K key , boolean create)
LinkedTreeMap::findByEntry( Entry<?,?> entry)
LinkedTreeMap::findByObject( Object key)
LinkedTreeMap::get( Object key)
LinkedTreeMap::keySet()
LinkedTreeMap::put( K key , V value)
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

=== STUB ===
```java
private void rebalance(Node<K, V> unbalanced, boolean insert) {
    // TODO: implement according to the specification
}
```
