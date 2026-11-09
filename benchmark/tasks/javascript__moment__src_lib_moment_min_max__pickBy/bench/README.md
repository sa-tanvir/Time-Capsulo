The driver bundles `/w/src/moment.js` with rollup, exposing the module-private `pickBy` of `src/lib/moment/min-max.js` through one appended export line, and calls `pickBy(fn, moments)` directly.
Workload: lists of UTC moments (`moment.utc(ms)`, `null` -> `moment.invalid()`), with `fn` = `'isBefore'` (min) or `'isAfter'` (max), passed either flat or wrapped in one array; random values, many-ties lists, sorted lists, scattered invalid moments.
S also holds the min/max test-suite patterns. Moments are built outside the timed region; the digest records which list element is returned (identity).
List length grows ~10 / ~100 / ~1000 for S / M / L (empty lists are excluded: they return the current time).
