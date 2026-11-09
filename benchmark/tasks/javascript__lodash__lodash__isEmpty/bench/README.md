Calls the public `_.isEmpty(value)` from `require('/w/lodash.js')` once per prebuilt value.
Workload: primitives, arrays, strings, `arguments`, typed arrays, Buffers, splice-style query collections, Maps, Sets, plain objects, functions with props, `{length}` objects (incl. invalid lengths on the prototype), constructor prototype objects with many keys, and instances whose 4-level prototype chain carries many enumerable keys while having no (or one) own key.
The size-dependent work is in the prototype-object and inherited-keys cases (keys per case ~50-100 / 500-1,000 / 5,000-10,000 for S/M/L); 400 random cases each, S also holds the test-suite edge values.
The digest covers each boolean result (and its type).
