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

// ---- listWeekdaysImpl(localeSorted, format, index, field). Each case: [locale, field, [args...]]
// where args are the first three arguments ({"$undef":1} -> undefined). Cases are grouped by locale;
// the global locale is switched (moment.locale) only when it changes. Three extra locales are
// defined once: 'tc-num' (week starts Wednesday), 'tc-fmt' (format/standalone weekday names chosen
// by an isFormat regex, Monday start) and 'tc-fn' (weekdaysShort/weekdaysMin given as functions).
// No case passes a non-boolean, non-number first argument (that path reads the current weekday).
function dec(v) { return (v !== null && typeof v === 'object' && '$undef' in v) ? undefined : v; }
loadLib([['listWeekdaysImpl', 'listWeekdaysImpl', '/w/src/lib/locale/lists', true]]).then(function (lib) {
    var f = lib.listWeekdaysImpl, moment = lib.moment, cur = null;
    moment.defineLocale('tc-num', {
        weekdays: 'one_two_three_four_five_six_seven'.split('_'),
        weekdaysShort: 'on_tw_th_fo_fi_si_se'.split('_'),
        weekdaysMin: '1_2_3_4_5_6_7'.split('_'),
        week: { dow: 3, doy: 6 }
    });
    moment.defineLocale('tc-fmt', {
        weekdays: {
            format: 'sundayF_mondayF_tuesdayF_wednesdayF_thursdayF_fridayF_saturdayF'.split('_'),
            standalone: 'Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday'.split('_'),
            isFormat: /\[ ?[Oo]n ?(?:last|next|this)? ?\] ?dddd/
        },
        week: { dow: 1, doy: 4 }
    });
    moment.defineLocale('tc-fn', {
        weekdaysShort: function (m, format) { return (/-ddd-/.test(format) ? 'x' : 'y') + (m === true ? 'L' : m ? m.day() : 'A'); },
        weekdaysMin: function (m, format) { return format + '|' + (m && m !== true ? m.day() : '?'); },
        week: { dow: 6, doy: 12 }
    });
    moment.locale('en');
    run(WORKLOAD,
        function (c) { return { loc: c[0], field: c[1], a: c[2].map(dec) }; },
        function (x) {
            if (x.loc !== cur) { moment.locale(x.loc); cur = x.loc; }
            return f(x.a[0], x.a[1], x.a[2], x.field);
        },
        function (x, r) { return typeof r + ':' + JSON.stringify(r); });
}).catch(fail);
