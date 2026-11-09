'use strict';
// Bench driver for lodash equalObjects. argv: <size> <repeat> <mode: check|time>
// equalObjects is internal; it is reached through the public _.isEqual, _.isEqualWith and _.isMatch
// (partial mode). The compared values are wide objects (many keys) or objects of small objects, so
// equalObjects does most of the work.
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');

function lcg(seed) {
    var s = seed >>> 0;
    return function () { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
}
function prim(rnd) {
    var r = rnd();
    return r < 0.6 ? Math.floor(r * 1000) : r < 0.8 ? 's' + Math.floor(r * 100) : r < 0.85 ? NaN : r < 0.9 ? null : r < 0.95 ? undefined : true;
}
function Foo() {}
function Bar() {}
function makeArgs() { return arguments; }
var SYMS = []; for (var q = 0; q < 16; q++) { SYMS.push(Symbol('s' + q)); }

function fill(target, keys, vals) { for (var i = 0; i < keys.length; i++) { target[keys[i]] = vals[i]; } return target; }
function rev(a) { return a.slice().reverse(); }

function build(c) {
    var rnd = lcg(c.seed), n = c.n, i, keys = [], vals = [], a, b, fn = 'eq', cust;
    for (i = 0; i < n; i++) { keys.push('k' + i + (i % 3 ? '' : '_' + Math.floor(rnd() * 99))); }
    var nested = c.kind === 'nested' || c.kind === 'instances';
    var m = nested ? Math.ceil(n / 4) : n;
    keys = keys.slice(0, m);
    for (i = 0; i < m; i++) {
        vals.push(c.kind === 'nested' ? { v: prim(rnd), w: 's' + i, x: i }
            : c.kind === 'instances' ? fill(new Foo(), ['v', 'w'], [prim(rnd), i]) : prim(rnd));
    }
    var copyVal = function (v) { return v && typeof v === 'object' ? fill(Object.create(Object.getPrototypeOf(v)), Object.keys(v), Object.keys(v).map(function (k) { return v[k]; })) : v; };
    var bvals = vals.map(copyVal);
    switch (c.kind) {
        case 'nullproto':
            a = fill(Object.create(null), keys, vals); b = fill({}, rev(keys), rev(bvals)); break;
        case 'args':
            a = makeArgs.apply(null, vals); b = fill({}, vals.map(function (v, k) { return String(k); }), bvals); break;
        case 'symbols':
            a = fill({}, keys, vals); b = fill({}, rev(keys), rev(bvals));
            SYMS.forEach(function (s, k) { a[s] = { z: k }; b[s] = { z: k }; });
            Object.defineProperty(b, Symbol('hidden'), { value: 1, enumerable: false });
            break;
        case 'match':
            fn = 'match';
            a = fill(Object.create({ inherited: 1, k0: 'shadowed' }), keys, vals);
            var half = keys.filter(function (k, idx) { return idx % 2 === 0; });
            b = fill({ inherited: 1 }, half, half.map(function (k) { return copyVal(a[k]); }));
            break;
        default:
            a = fill({}, keys, vals); b = fill({}, rev(keys), rev(bvals));
    }
    if (c.kind === 'cyclic') { a.self = a; b.self = b; a.pair = b; b.pair = a; }
    if (c.kind === 'custom') {
        fn = 'with';
        cust = function (x, y) { return typeof x === 'string' && typeof y === 'string' ? x.toLowerCase() === y.toLowerCase() : undefined; };
        Object.keys(b).forEach(function (k) { if (typeof b[k] === 'string') { b[k] = b[k].toUpperCase(); } });
    }
    var bk = Object.keys(b).filter(function (k) { return k !== 'self' && k !== 'pair' && k !== 'inherited'; });
    if (c.variant === 'diff' && bk.length) {
        b[bk[Math.floor(rnd() * bk.length)]] = { changed: true };
    } else if (c.variant === 'extra') {
        b.extraKey = 0;
    } else if (c.variant === 'ctor') {
        if (c.kind === 'instances' && bk.length) {
            var k0 = bk[Math.floor(rnd() * bk.length)];
            b[k0] = fill(new Bar(), Object.keys(b[k0]), Object.keys(b[k0]).map(function (k) { return b[k0][k]; }));
        } else if (c.kind === 'wide' || c.kind === 'custom') {
            Object.setPrototypeOf(b, Foo.prototype);
        } else if (c.kind === 'nested') {
            b.constructor = Foo; a.constructor = Foo;   // compared as an ordinary key
        }
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
    var o1 = { a: [1, 2], b: null }, o2 = { a: [1, 2], b: null }, log = [];
    o1.b = o2; o2.b = o1;
    _.isEqualWith(o1, o2, function () { log.push(arguments.length + ':' + String(arguments[2])); });
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
