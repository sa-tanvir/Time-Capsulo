def _get_values(self, value):
    """
    Helper to yield items from the parent iterator that match *value*.
    Items that don't match are stored in the local cache as they
    are encountered.
    """
    while True:
        # If we've cached some items that match the target value, emit
        # the first one and evict it from the cache.
        if self._cache[value]:
            yield self._cache[value].popleft()
        # Otherwise we need to advance the parent iterator to search for
        # a matching item, caching the rest.
        else:
            while True:
                try:
                    item = next(self._it)
                except StopIteration:
                    return
                item_value = self._key(item)
                if item_value == value:
                    yield item
                    break
                elif self._validator(item_value):
                    self._cache[item_value].append(item)
