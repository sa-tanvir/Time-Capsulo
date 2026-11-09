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
LinkedHashTreeMap::find( K key , boolean create)
LinkedHashTreeMap::findByEntry( Entry<?,?> entry)
LinkedHashTreeMap::findByObject( Object key)
LinkedHashTreeMap::get( Object key)
LinkedHashTreeMap::keySet()
LinkedHashTreeMap::put( K key , V value)
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
