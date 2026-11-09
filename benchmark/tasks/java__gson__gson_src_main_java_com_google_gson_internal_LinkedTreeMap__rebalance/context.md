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
