Node<K, V> find(K key, boolean create) {
  Comparator<? super K> comparator = this.comparator;
  Node<K, V> nearest = root;
  int comparison = 0;

  if (nearest != null) {
    // Micro-optimization: avoid polymorphic calls to Comparator.compare().
    @SuppressWarnings("unchecked") // Throws a ClassCastException below if there's trouble.
        Comparable<Object> comparableKey = (comparator == NATURAL_ORDER)
        ? (Comparable<Object>) key
        : null;

    while (true) {
      comparison = (comparableKey != null)
          ? comparableKey.compareTo(nearest.key)
          : comparator.compare(key, nearest.key);

      // We found the requested key.
      if (comparison == 0) {
        return nearest;
      }

      // If it exists, the key is in a subtree. Go deeper.
      Node<K, V> child = (comparison < 0) ? nearest.left : nearest.right;
      if (child == null) {
        break;
      }

      nearest = child;
    }
  }

  // The key doesn't exist in this tree.
  if (!create) {
    return null;
  }

  // Create the node and add it to the tree or the table.
  Node<K, V> header = this.header;
  Node<K, V> created;
  if (nearest == null) {
    // Check that the value is comparable if we didn't do any comparisons.
    if (comparator == NATURAL_ORDER && !(key instanceof Comparable)) {
      throw new ClassCastException(key.getClass().getName() + " is not Comparable");
    }
    created = new Node<K, V>(nearest, key, header, header.prev);
    root = created;
  } else {
    created = new Node<K, V>(nearest, key, header, header.prev);
    if (comparison < 0) { // nearest.key is higher
      nearest.left = created;
    } else { // comparison > 0, nearest.key is lower
      nearest.right = created;
    }
    rebalance(nearest, true);
  }
  size++;
  modCount++;

  return created;
}
