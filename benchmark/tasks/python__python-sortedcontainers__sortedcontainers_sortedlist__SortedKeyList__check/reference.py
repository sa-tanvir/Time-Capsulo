def _check(self):
    """Check invariants of sorted-key list.

    Runtime complexity: `O(n)`

    """
    try:
        assert self._load >= 4
        assert len(self._maxes) == len(self._lists) == len(self._keys)
        assert self._len == sum(len(sublist) for sublist in self._lists)

        # Check all sublists are sorted.

        for sublist in self._keys:
            for pos in range(1, len(sublist)):
                assert sublist[pos - 1] <= sublist[pos]

        # Check beginning/end of sublists are sorted.

        for pos in range(1, len(self._keys)):
            assert self._keys[pos - 1][-1] <= self._keys[pos][0]

        # Check _keys matches _key mapped to _lists.

        for val_sublist, key_sublist in zip(self._lists, self._keys):
            assert len(val_sublist) == len(key_sublist)
            for val, key in zip(val_sublist, key_sublist):
                assert self._key(val) == key

        # Check _maxes index is the last value of each sublist.

        for pos in range(len(self._maxes)):
            assert self._maxes[pos] == self._keys[pos][-1]

        # Check sublist lengths are less than double load-factor.

        double = self._load << 1
        assert all(len(sublist) <= double for sublist in self._lists)

        # Check sublist lengths are greater than half load-factor for all
        # but the last sublist.

        half = self._load >> 1
        for pos in range(0, len(self._lists) - 1):
            assert len(self._lists[pos]) >= half

        if self._index:
            assert self._len == self._index[0]
            assert len(self._index) == self._offset + len(self._lists)

            # Check index leaf nodes equal length of sublists.

            for pos in range(len(self._lists)):
                leaf = self._index[self._offset + pos]
                assert leaf == len(self._lists[pos])

            # Check index branch nodes are the sum of their children.

            for pos in range(self._offset):
                child = (pos << 1) + 1
                if child >= len(self._index):
                    assert self._index[pos] == 0
                elif child + 1 == len(self._index):
                    assert self._index[pos] == self._index[child]
                else:
                    child_sum = self._index[child] + self._index[child + 1]
                    assert child_sum == self._index[pos]
    except:
        import sys
        import traceback
        traceback.print_exc(file=sys.stdout)
        print('len', self._len)
        print('load', self._load)
        print('offset', self._offset)
        print('len_index', len(self._index))
        print('index', self._index)
        print('len_maxes', len(self._maxes))
        print('maxes', self._maxes)
        print('len_keys', len(self._keys))
        print('keys', self._keys)
        print('len_lists', len(self._lists))
        print('lists', self._lists)
        raise
