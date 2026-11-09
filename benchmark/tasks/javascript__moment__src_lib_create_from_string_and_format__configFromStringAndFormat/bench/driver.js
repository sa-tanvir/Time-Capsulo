'use strict';
// Bench driver for moment 2.24.0. argv: <size> <repeat> <mode: check|time>
// The target is not exported by moment's public build, so the driver bundles a tiny entry module
// (`import moment from '/w/src/moment'` + the target from its source file) with the repo's rollup
// into an IIFE and evaluates it with `module`/`require` undefined (no lazy locale loading from disk).
// All library state (locales, hooks) is the normal state set up by src/moment.js; moment.now is pinned to
// 2019-01-21T12:00:00Z. TZ=UTC in the image.
var fs = require('fs');
var path = require('path');
var crypto = require('crypto');
var rollup = require('/w/node_modules/rollup').rollup;

var SIZE = process.argv[2];
var REPEAT = parseInt(process.argv[3], 10);
var MODE = process.argv[4];
var WORKLOAD = JSON.parse(fs.readFileSync(path.join(__dirname, 'workload_' + SIZE + '.json'), 'utf8'));

function loadLib(imports) {
    // imports: [[localName, importedName ('default' | a named export | a module-private name), '/w/src/lib/...', isPrivate]]
    // Module-private targets are exposed by appending one export line to their module when rollup loads it.
    var entry = '/tmp/tcbench_entry_' + process.pid + '.js';
    var extra = {};
    var src = "import moment from '/w/src/moment';\n";
    imports.forEach(function (im) {
        var file = im[2] + '.js';
        if (im[3]) {
            extra[file] = (extra[file] || '') + '\nexport { ' + im[1] + ' as __tc_' + im[1] + ' };\n';
            src += 'import { __tc_' + im[1] + ' as ' + im[0] + " } from '" + im[2] + "';\n";
        } else if (im[1] === 'default') {
            src += 'import ' + im[0] + " from '" + im[2] + "';\n";
        } else {
            src += 'import { ' + im[1] + ' as ' + im[0] + " } from '" + im[2] + "';\n";
        }
    });
    src += 'export { moment, ' + imports.map(function (im) { return im[0]; }).join(', ') + ' };\n';
    fs.writeFileSync(entry, src);
    var plugin = { name: 'tc-expose', load: function (id) {
        return extra[id] ? fs.readFileSync(id, 'utf8') + extra[id] : null;
    } };
    return rollup({ input: entry, plugins: [plugin], onwarn: function () {} })
        .then(function (b) { return b.generate({ format: 'iife', name: 'tcb' }); })
        .then(function (r) {
            fs.unlinkSync(entry);
            /* jshint evil:true */
            var lib = new Function('module', 'exports', 'define', 'require', r.code + '\nreturn tcb;')();
            // Freeze the library clock (moment.now is the documented override hook): any defaulting
            // to "today" inside moment then yields 2019-01-21T12:00:00Z, so outputs are reproducible.
            lib.moment.now = function () { return 1548072000000; };
            return lib;
        });
}

function errKind(e) { return 'ERR:' + (e && e.name); }

// run(cases, prepare, call, canon): prepare(case) builds fresh arguments (outside the timed region),
// call(args) invokes the target, canon(args, result) gives the canonical output string for check mode.
function run(cases, prepare, call, canon) {
    var i, args, res;
    if (MODE === 'check') {
        var h = crypto.createHash('sha256');
        for (i = 0; i < cases.length; i++) {
            args = prepare(cases[i]);
            try { res = canon(args, call(args)); } catch (e) { res = errKind(e); }
            h.update(i + ':' + res + '\n');
        }
        console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
        return;
    }
    var elapsed = 0, keep = 0, r, all, t0, dt;
    for (r = 0; r < REPEAT; r++) {
        all = cases.map(prepare);
        t0 = process.hrtime();
        for (i = 0; i < all.length; i++) {
            try { res = call(all[i]); keep += res ? 1 : 0; } catch (e) { keep += 2; }
        }
        dt = process.hrtime(t0);
        elapsed += dt[0] + dt[1] / 1e9;
    }
    process.stderr.write('checksum ' + keep + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: REPEAT, elapsed_s: elapsed }));
}

function fail(e) { console.error(e && e.stack || e); process.exit(1); }

// ---- configFromStringAndFormat(config): parses config._i with the format config._f into config
// (config._a, config._d, parsing flags in config._pf, ...). Workload: {"cases": [[input, format, strict, utc, locale], ...]};
// format '$ISO' / '$RFC' stand for moment.ISO_8601 / moment.RFC_2822. A fresh config is built for every call
// (outside the timed region); the digest covers the whole config afterwards.

// ---- Shared by the config-parsing drivers. A case is [input, format, strict, utc, locale]
// (format may be a string, an array of strings, or {"$undef":1}). makeConfig builds the config object
// exactly as createLocalOrUTC/prepareConfig do before dispatching (fresh object per call).
// canonConfig serialises every own property of the config after the call (sorted keys, recursively;
// Dates as their time value, the locale as its abbreviation, undefined values omitted).
function dec(v) { return (v !== null && typeof v === 'object' && !Array.isArray(v) && '$undef' in v) ? undefined : v; }
function makeConfig(c, locs) {
    var utc = !!c[3];
    return { _isAMomentObject: true, _useUTC: utc, _isUTC: utc, _l: undefined, _i: c[0],
        _f: Array.isArray(c[1]) ? c[1].slice() : dec(c[1]), _strict: dec(c[2]), _locale: locs[c[4]] };
}
function canonValue(v, depth) {
    if (v === undefined) { return undefined; }
    if (v === null || typeof v !== 'object') {
        if (typeof v === 'function') { return 'fn'; }
        if (typeof v === 'number' && !isFinite(v)) { return 'num:' + String(v); }
        return v;
    }
    if (v instanceof Date) { return 'date:' + String(v.getTime()); }
    if (v._abbr !== undefined && v._config !== undefined) { return 'locale:' + v._abbr; }
    if (Array.isArray(v)) {
        var a = [];
        for (var i = 0; i < v.length; i++) { var x = canonValue(v[i], depth + 1); a.push(x === undefined ? null : x); }
        return a;
    }
    var o = {};
    Object.keys(v).sort().forEach(function (k) { var x = canonValue(v[k], depth + 1); if (x !== undefined) { o[k] = x; } });
    return o;
}
function canonConfig(cfg, r) {
    return JSON.stringify([canonValue(cfg, 1), canonValue(r, 1)]);
}
function defineLocales(moment) {
    moment.defineLocale('tc-fr', {
        months: 'janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split('_'),
        monthsShort: 'janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.'.split('_'),
        monthsParseExact: true,
        weekdays: 'dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi'.split('_'),
        weekdaysShort: 'dim._lun._mar._mer._jeu._ven._sam.'.split('_'),
        weekdaysMin: 'di_lu_ma_me_je_ve_sa'.split('_'),
        weekdaysParseExact: true,
        longDateFormat: { LT: 'HH:mm', LTS: 'HH:mm:ss', L: 'DD/MM/YYYY', LL: 'D MMMM YYYY',
            LLL: 'D MMMM YYYY HH:mm', LLLL: 'dddd D MMMM YYYY HH:mm' },
        meridiemParse: /PD|MD/,
        isPM: function (input) { return input.charAt(0) === 'M'; },
        meridiem: function (hours) { return hours < 12 ? 'PD' : 'MD'; },
        week: { dow: 1, doy: 4 }
    });
    moment.locale('en');
    return { en: moment.localeData('en'), 'tc-fr': moment.localeData('tc-fr') };
}

loadLib([['configFromStringAndFormat', 'configFromStringAndFormat', '/w/src/lib/create/from-string-and-format']]).then(function (lib) {
    var f = lib.configFromStringAndFormat, locs = defineLocales(lib.moment);
    var cases = WORKLOAD.cases.map(function (c) {
        if (c[1] === '$ISO') { c = c.slice(); c[1] = lib.moment.ISO_8601; }
        if (c[1] === '$RFC') { c = c.slice(); c[1] = lib.moment.RFC_2822; }
        return c;
    });
    run(cases, function (c) { return makeConfig(c, locs); },
        function (cfg) { return f(cfg); },
        canonConfig);
}).catch(fail);
