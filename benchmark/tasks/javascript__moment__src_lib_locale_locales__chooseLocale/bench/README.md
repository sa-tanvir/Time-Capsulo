The driver bundles `/w/src/moment.js` with rollup, exposing the module-private `chooseLocale` of `src/lib/locale/locales.js` through one appended export line, defines 22 locales (plus built-in 'en'), and calls `chooseLocale(names)`.
The bundle is evaluated without `module`/`require`, so no locale files are loaded from disk: only defined locales are found.
Workload: lists of requested names mixing known locales, unknown variants of known roots, unknown roots, upper case and '_' separators, with real candidates biased to the end of the list; S also has the moment.locale([...]) test-suite lists.
List length grows ~3 / ~30 / ~300 names for S / M / L.
