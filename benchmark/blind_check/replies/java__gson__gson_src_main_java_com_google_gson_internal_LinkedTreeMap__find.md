```java
Node<K, V> find(K key, boolean create) {
    Comparator<? super K> comparator = this.comparator;
    Node<K, V> nearest = root;
    int comparison = 0;

    if (nearest != null) {
        @SuppressWarnings("unchecked")
        Comparable<Object> comparableKey = (comparator == NATURAL_ORDER)
            ? (Comparable<Object>) key
            : null;
        while (true) {
            comparison = (comparableKey != null)
                ? comparableKey.compareTo(nearest.key)
                : comparator.compare(key, nearest.key);
            if (comparison == 0) {
                return nearest;
            }
            Node<K, V> child = (comparison < 0) ? nearest.left : nearest.right;
            if (child == null) {
                break;
            }
            nearest = child;
        }
    }

    if (!create) {
        return null;
    }

    Node<K, V> header = this.header;
    Node<K, V> created;
    if (nearest == null) {
        if (comparator == NATURAL_ORDER && !(key instanceof Comparable)) {
            throw new ClassCastException(key.getClass().getName() + " is not Comparable");
        }
        created = new Node<K, V>(null, key, header, header.prev);
        root = created;
    } else {
        created = new Node<K, V>(nearest, key, header, header.prev);
        if (comparison < 0) {
            nearest.left = created;
        } else {
            nearest.right = created;
        }
        rebalance(nearest, true);
    }
    size++;
    modCount++;
    return created;
}
```
