'use strict';
// Bench driver for lodash baseDifference. argv: <size> <repeat> <mode: check|time>
// The target is internal; it is reached through the public wrappers _.difference / _.differenceBy / _.differenceWith
// (from require('/w/lodash.js')), which only flatten / validate their arguments and delegate to it.
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');
var OP = 'difference';

function lcg(seed) {
    var s = seed >>> 0;
    return function () { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
}
var SYMS = [Symbol('a'), Symbol('b'), Symbol.iterator, Symbol('c')];

function makeElem(kind, k, pool, rnd) {
    switch (kind) {
        case 'num': return k === 0 ? (rnd() < 0.5 ? -0 : 0) : k === 1 ? NaN : k;
        case 'str': return 's' + k;
        case 'obj': return pool[k];
        case 'float': return k + Math.floor(rnd() * 100) / 100;
        default: {
            var r = k % 9;
            return r === 0 ? null : r === 1 ? undefined : r === 2 ? (k & 16) === 0 : r === 3 ? SYMS[k % 4]
                : r === 4 ? String(k) : r === 5 ? NaN : r === 6 ? -0 : k;
        }
    }
}

function floorKey(v) { return typeof v === 'number' ? Math.floor(v) : v; }

function build(c) {
    var rnd = lcg(c.seed), pool = [];
    if (c.kind === 'obj') { for (var p = 0; p < c.dom; p++) { pool.push({ id: p }); } }
    var arrays = c.lens.map(function (len) {
        var a = new Array(len);
        for (var i = 0; i < len; i++) { a[i] = makeElem(c.kind, Math.floor(rnd() * c.dom), pool, rnd); }
        return a;
    });
    var extra;
    if (c.mode === 'by') { extra = c.kind === 'obj' ? 'id' : floorKey; }
    else if (c.mode === 'with') { extra = c.kind === 'obj' ? function (a, b) { return a.id === b.id; } : _.eq; }
    if (c.mode === 'by' && c.kind === 'obj') {   // fresh copies so only the iteratee can match them
        arrays = arrays.map(function (a, idx) { return idx === 0 ? a : a.map(function (o) { return { id: o.id }; }); });
    }
    return { arrays: arrays, mode: c.mode, extra: extra };
}

function call(c) {
    var A = c.arrays;
    if (OP === 'uniq') {
        return c.mode === 'plain' ? _.uniq(A[0]) : c.mode === 'by' ? _.uniqBy(A[0], c.extra) : _.uniqWith(A[0], c.extra);
    }
    var name = OP + (c.mode === 'plain' ? '' : c.mode === 'by' ? 'By' : 'With');
    return c.mode === 'plain' ? _[name].apply(_, A) : _[name].apply(_, A.concat([c.extra]));
}

function canon(v) {
    if (v === undefined) { return 'u'; }
    if (typeof v === 'number') { return v === 0 && 1 / v < 0 ? '-0' : String(v); }
    if (typeof v === 'symbol') { return 'y' + String(v); }
    if (typeof v === 'string') { return 's' + v; }
    if (v && typeof v === 'object') { return 'o' + v.id; }
    return String(v);
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
        try {
            var res = call(cases[i]);
            // identity of kept objects matters: they must come from the first array
            var first = new Set(cases[i].arrays[0]);
            o = res.map(function (v) { return canon(v) + (v && typeof v === 'object' ? (first.has(v) ? '#' : '!') : ''); }).join(',');
        } catch (e) { o = 'ERR:' + e.name; }
        h.update(o + '\n');
    }
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) { acc += call(cases[j]).length; }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
