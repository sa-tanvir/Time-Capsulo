'use strict';
// Bench driver for lodash equalArrays. argv: <size> <repeat> <mode: check|time>
// equalArrays is internal; it is reached through the public _.isEqual / _.isEqualWith (ordered; maps and
// sets go through it in unordered mode) and _.isMatch (partial + unordered). The values are arrays of
// primitives or of small arrays, typed arrays, sets and maps, so equalArrays does most of the work.
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');

function lcg(seed) {
    var s = seed >>> 0;
    return function () { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
}
function prim(rnd) {
    var r = rnd();
    return r < 0.6 ? Math.floor(r * 1000) : r < 0.8 ? 's' + Math.floor(r * 100) : r < 0.85 ? NaN : r < 0.9 ? null : r < 0.95 ? -0 : true;
}

function build(c) {
    var rnd = lcg(c.seed), n = c.n, i, a = [], b, fn = 'eq', cust;
    var un = Math.max(Math.floor(n / 50), c.n < 4 ? c.n : 0);
    switch (c.kind) {
        case 'flat': case 'custom': case 'cyclic':
            for (i = 0; i < n; i++) { a.push(prim(rnd)); }
            b = a.slice();
            if (c.kind === 'cyclic') { a.push(a); b.push(b); }
            if (c.kind === 'custom') {
                fn = 'with';
                cust = function (x, y) { return typeof x === 'string' && typeof y === 'string' ? x.toLowerCase() === y.toLowerCase() : undefined; };
                b = b.map(function (v) { return typeof v === 'string' ? v.toUpperCase() : v; });
            }
            break;
        case 'nested':
            for (i = 0; i < n / 4; i++) { a.push([prim(rnd), prim(rnd), i]); }
            b = a.map(function (x) { return x.slice(); });
            break;
        case 'typed':
            a = new Float64Array(n); for (i = 0; i < n; i++) { a[i] = Math.floor(rnd() * 1e6) / 8; }
            b = new Float64Array(a);
            break;
        case 'sparse':
            a = new Array(n); for (i = 0; i < n; i++) { if (rnd() < 0.5) { a[i] = Math.floor(rnd() * 50); } }
            b = new Array(n); for (i = 0; i < n; i++) { b[i] = a[i]; }   // dense copy (holes -> undefined)
            a.extra = 1; b.extra = 2;                                    // non-index props are ignored
            break;
        case 'set': case 'map': case 'match': {
            var vals = [];
            for (i = 0; i < un; i++) { vals.push(c.kind === 'set' ? i * 7 + (i % 3) : [i % 13, 's' + (i % 5)]); }
            var shuffled = vals.slice();
            for (i = shuffled.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = shuffled[i]; shuffled[i] = shuffled[j]; shuffled[j] = t; }
            if (c.kind === 'set') { a = new Set(vals); b = shuffled; }
            else if (c.kind === 'map') { a = vals; b = shuffled; }
            else { fn = 'match'; a = { a: vals }; b = { a: shuffled.slice(0, Math.ceil(shuffled.length * 0.7)) }; }
            break;
        }
    }
    // variants
    if (c.kind === 'set') {
        var bb = b.slice();
        if (c.variant === 'diff' && bb.length) { bb[Math.floor(rnd() * bb.length)] = -1; }
        if (c.variant === 'len') { bb.push(-5); }
        return { a: a, b: new Set(bb), fn: fn };
    }
    if (c.kind === 'map') {
        var ma = new Map(), mb = new Map();
        a.forEach(function (e, k) { ma.set('k' + k, e); });
        b.forEach(function (e) { mb.set('k' + a.indexOf(e), e.slice()); });
        if (c.variant === 'diff' && b.length) { mb.set('k' + Math.floor(rnd() * b.length), ['x']); }
        if (c.variant === 'len') { mb.set('extra', 1); }
        return { a: ma, b: mb, fn: fn };
    }
    var target = c.kind === 'match' ? b.a : b;
    if (c.variant === 'diff' && target.length) {
        var p = Math.floor(rnd() * target.length);
        target[p] = c.kind === 'nested' ? [target[p][0], 'changed', -1] : c.kind === 'match' ? ['nope'] : -12345.5;
    } else if (c.variant === 'len') {
        if (c.kind === 'typed') { target = b = new Float64Array(Array.prototype.slice.call(b, 0, Math.max(b.length - 1, 0))); }
        else { target.push(0); }
    }
    return { a: a, b: b, fn: fn, cust: cust };
}

function call(c) {
    return c.fn === 'eq' ? _.isEqual(c.a, c.b) : c.fn === 'with' ? _.isEqualWith(c.a, c.b, c.cust) : _.isMatch(c.a, c.b);
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(build);

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var o;
        try { o = String(call(cases[i])) + '|' + String(cases[i].fn === 'eq' ? _.isEqual(cases[i].b, cases[i].a) : ''); } catch (e) { o = 'ERR:' + e.name; }
        h.update(o + '\n');
    }
    // customizer call log on a small structure
    var log = [], x = [1, [2, 'a'], { k: 3 }], y = [1, [2, 'a'], { k: 3 }];
    _.isEqualWith(x, y, function () { log.push(arguments.length + ':' + typeof arguments[0] + ':' + String(arguments[2])); });
    h.update(log.join(','));
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) { if (call(cases[j])) { acc++; } }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
