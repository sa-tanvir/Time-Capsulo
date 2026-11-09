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

// ---- Locale#monthsParse = localeMonthsParse(monthName, format, strict), called with `this` = a Locale.
// Workload: {"times": k, "cases": [[locale, name, format, strict], ...]} ({"$undef":1} -> undefined);
// the case list is used k times. Locales are defined once by the driver (below) and keep their lazily
// built lookup caches across calls, as in real use (check mode starts with cold caches).
function dec(v) { return (v !== null && typeof v === 'object' && '$undef' in v) ? undefined : v; }
loadLib([['localeMonthsParse', 'localeMonthsParse', '/w/src/lib/units/month']]).then(function (lib) {
    var f = lib.localeMonthsParse, moment = lib.moment, locs = {}, cases = [], k, i;
    var fr = {
        months: 'janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split('_'),
        monthsShort: 'janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.'.split('_')
    };
    function ruParse() { return [/^янв/i, /^фев/i, /^мар/i, /^апр/i, /^ма[йя]/i, /^июн/i, /^июл/i, /^авг/i, /^сен/i, /^окт/i, /^ноя/i, /^дек/i]; }
    var defs = {
        'tc-fr': fr,
        'tc-fr-exact': Object.assign({}, fr, { monthsParseExact: true }),
        'tc-ru': {
            months: {
                format: 'января_февраля_марта_апреля_мая_июня_июля_августа_сентября_октября_ноября_декабря'.split('_'),
                standalone: 'январь_февраль_март_апрель_май_июнь_июль_август_сентябрь_октябрь_ноябрь_декабрь'.split('_')
            },
            monthsShort: 'янв._февр._мар._апр._мая_июня_июля_авг._сент._окт._нояб._дек.'.split('_'),
            monthsParse: ruParse(), longMonthsParse: ruParse(), shortMonthsParse: ruParse()
        },
        'tc-fmt': {
            months: {
                format: 'ofJan_ofFeb_ofMar_ofApr_ofMay_ofJun_ofJul_ofAug_ofSep_ofOct_ofNov_ofDec'.split('_'),
                standalone: 'Jan.uary_Feb.ruary_March_April_May_June_July_August_September_October_November_December'.split('_')
            },
            monthsShort: 'J.n_F.b_M.r_A.r_M.y_J.n_J.l_A.g_S.p_O.t_N.v_D.c'.split('_')
        },
        'tc-prefix-exact': {
            months: 'A_AA_AAA_B_B B_BB  B_C_C-C_C,C2C_D_D+D_D`D*D'.split('_'),
            monthsShort: 'E_EE_EEE_F_FF_FFF_G_GG_GGG_H_HH_HHH'.split('_'),
            monthsParseExact: true
        }
    };
    Object.keys(defs).forEach(function (n) { moment.defineLocale(n, defs[n]); });
    moment.locale('en');
    ['en'].concat(Object.keys(defs)).forEach(function (n) { locs[n] = moment.localeData(n); });
    var base = WORKLOAD.cases.map(function (c) { return [locs[c[0]], dec(c[1]), dec(c[2]), dec(c[3])]; });
    for (k = 0; k < WORKLOAD.times; k++) { for (i = 0; i < base.length; i++) { cases.push(base[i]); } }
    run(cases, function (c) { return c; },
        function (c) { return f.call(c[0], c[1], c[2], c[3]); },
        function (c, r) { return typeof r + ':' + String(r); });
}).catch(fail);
