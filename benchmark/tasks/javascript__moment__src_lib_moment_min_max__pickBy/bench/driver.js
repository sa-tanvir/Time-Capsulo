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

// ---- pickBy(fn, moments). Each case: [fn ('isBefore'|'isAfter'), wrapped (bool), [epoch ms | null]]
// null -> an invalid moment. wrapped -> moments = [[m0, m1, ...]] (the moment.min([...]) form).
// The moments are built (moment.utc) outside the timed region; output = index of the returned
// object in the flat list (identity), plus its validity and value. No empty lists (those would
// return the current time).
loadLib([['pickBy', 'pickBy', '/w/src/lib/moment/min-max', true]]).then(function (lib) {
    var f = lib.pickBy, moment = lib.moment;
    function prepare(c) {
        var flat = c[2].map(function (ms) { return ms === null ? moment.invalid() : moment.utc(ms); });
        return { fn: c[0], flat: flat, arg: c[1] ? [flat] : flat };
    }
    run(WORKLOAD, prepare,
        function (a) { return f(a.fn, a.arg); },
        function (a, r) {
            return a.flat.indexOf(r) + ':' + (r && r.isValid ? r.isValid() + ':' + r.valueOf() : typeof r);
        });
}).catch(fail);
