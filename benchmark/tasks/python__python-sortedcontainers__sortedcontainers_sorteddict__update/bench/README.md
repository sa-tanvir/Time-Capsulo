Workload: seeded recipes (S 40 / M 24 / L 16 cases) with base sizes up to 1e3 / 1e4 / 1e5 keys and update batches
from 0.05% to 200% of the base size; forms: dict, list of pairs, kwargs, pairs+kwargs, SortedDict, empty call;
int or string keys, with or without a `neg` key function, ~1/8 of cases start from an empty dict.
The driver expands each recipe deterministically, builds the receiver without calling `update`, then times only
`sd.update(*args, **kwargs)`; check mode hashes the resulting items and the key-list/dict lengths.
