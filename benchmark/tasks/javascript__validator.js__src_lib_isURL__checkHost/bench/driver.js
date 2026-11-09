'use strict';
// Bench driver for validator.js checkHost (src/lib/isURL.js). argv: <size> <repeat> <mode: check|time>
// The source file is transpiled with the repo's Babel config (as @babel/register does for the
// tests) with one extra line exporting the target, so non-exported helpers can be called directly.
process.env.BABEL_DISABLE_CACHE = '1';
var fs = require('fs');
var crypto = require('crypto');
var Module = require('module');
process.chdir('/w');
require('/w/node_modules/@babel/register');
var babel = require('/w/node_modules/@babel/core');

function loadTarget(rel, name) {
    var file = '/w/' + rel;
    var src = fs.readFileSync(file, 'utf8') + '\nexport const __tcTarget = ' + name + ';\n';
    var code = babel.transformSync(src, { filename: file, cwd: '/w' }).code;
    var m = new Module(file, module);
    m.filename = file;
    m.paths = Module._nodeModulePaths(require('path').dirname(file));
    m._compile(code, file);
    return m.exports.__tcTarget;
}

var target = loadTarget('src/lib/isURL.js', 'checkHost');

// Workload values: plain JSON, plus {"$rep": [s, n]} -> s repeated n times, {"$cat": [a, b, ...]} -> concatenation, {"$re": [src, flags]} -> RegExp,
// {"$undef": 1} -> undefined, {"$obj": {...}} -> object with that literal content,
// {"$tostr": s} -> object whose toString() returns s, {"$notostr": 1} -> object without a toString function.
function decode(v) {
    if (Array.isArray(v)) { return v.map(decode); }
    if (v !== null && typeof v === 'object') {
        if ('$rep' in v) { return decode(v.$rep[0]).repeat(v.$rep[1]); }
        if ('$cat' in v) { return v.$cat.map(decode).join(''); }
        if ('$re' in v) { return new RegExp(v.$re[0], v.$re[1]); }
        if ('$undef' in v) { return undefined; }
        if ('$obj' in v) { var o = {}; Object.keys(v.$obj).forEach(function (k) { o[k] = decode(v.$obj[k]); }); return o; }
        if ('$tostr' in v) { var s = v.$tostr; return { toString: function () { return s; } }; }
        if ('$notostr' in v) { var p = Object.create(null); p.toString = 1; return p; }
        var r = {};
        Object.keys(v).forEach(function (k) { r[k] = decode(v[k]); });
        return r;
    }
    return v;
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));

function canon(out) {
    return typeof out + ':' + JSON.stringify(out);
}

if (mode === 'check') {
    var cases = decode(raw);
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var o;
        try {
            o = canon(target.apply(null, cases[i]));
        } catch (e) {
            o = 'ERR:' + e.name;
        }
        h.update(o + '\n');
    }
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var elapsed = 0;
    for (var r = 0; r < repeat; r++) {
        var cs = decode(raw); // fresh argument objects each pass (options objects may be filled in by the target)
        var t0 = process.hrtime();
        for (var j = 0; j < cs.length; j++) {
            try {
                acc += target.apply(null, cs[j]) ? 1 : 0;
            } catch (e) {
                acc += 2;
            }
        }
        var dt = process.hrtime(t0);
        elapsed += dt[0] + dt[1] / 1e9;
    }
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: raw.length, repeat: repeat, elapsed_s: elapsed }));
}
