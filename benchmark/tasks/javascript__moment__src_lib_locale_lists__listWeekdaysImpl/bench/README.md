The driver bundles `/w/src/moment.js` with rollup, exposing the module-private `listWeekdaysImpl` of `src/lib/locale/lists.js` through one appended export line, and calls it with the argument shapes of `moment.weekdays/weekdaysShort/weekdaysMin`.
Workload: 'en' plus three driver-defined locales (week starting Wednesday; format/standalone names with an isFormat regex; function-valued short/min names), all three fields, with/without locale sorting, formats and integer indexes (incl. negative and >= 7).
Cases are sorted by locale; the global locale is switched only when it changes. The non-boolean string first argument form is excluded (it depends on the current weekday).
Per-call work is bounded (<= 7 names), so S/M/L scale the call count: ~300 / 3,000 / 30,000.
