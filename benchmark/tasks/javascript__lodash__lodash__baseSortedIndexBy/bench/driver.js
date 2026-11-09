'use strict';
// Bench driver for lodash baseSortedIndexBy. argv: <size> <repeat> <mode: check|time>
// The target is internal; it is reached through the public wrappers, which add only O(1) work:
//   _.sortedIndexBy / _.sortedLastIndexBy(array, value, iteratee)  -> baseSortedIndexBy(array, value, f, false/true)
//   _.sortedIndex / _.sortedLastIndex(array, value) with a non-number value -> baseSortedIndexBy(array, value, identity, ...)
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');

function lcg(seed) {
    var s = seed >>> 0;
    return function () { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
}
var SYMS = [Symbol('a'), Symbol('b'), Symbol('c')];
function pad(k) { var s = String(k); while (s.length < 7) { s = '0' + s; } return 'k' + s; }

function build(c) {
    var rnd = lcg(c.seed), arr = [], i, v = 0, queries = [];
    for (i = 0; i < c.n; i++) {
        v += Math.floor(rnd() * 3);              // non-decreasing with duplicates
        arr.push(c.kind === 'str' ? pad(v) : c.kind === 'obj' ? { x: v } : v);
    }
    var top = v + 2;
    if (c.kind === 'mixed') {
        for (i = 0; i < c.special; i++) { arr.push(SYMS[i % 3]); }
        for (i = 0; i < c.special; i++) { arr.push(null); }
        for (i = 0; i < c.special; i++) { arr.push(undefined); }
        for (i = 0; i < c.special; i++) { arr.push(NaN); }
    }
    for (i = 0; i < c.q; i++) {
        var r = rnd(), num = Math.floor(rnd() * (top + 2)) - 1, val, how = i % 4;
        if (c.kind === 'str') { val = pad(num); }
        else if (c.kind === 'obj') { val = { x: num }; }
        else if (c.kind === 'num') { val = num; }
        else {
            val = r < 0.5 ? num : r < 0.6 ? SYMS[i % 3] : r < 0.7 ? null : r < 0.8 ? undefined : r < 0.9 ? NaN : String(num);
        }
        queries.push({ v: val, how: how });
    }
    return { arr: arr, kind: c.kind, queries: queries };
}

var byFn = function (o) { return o === undefined || o === null || typeof o !== 'object' ? o : o.x; };
function run(c, q) {
    if (c.kind === 'obj') {
        // property shorthand and function iteratee
        return q.how & 1 ? _.sortedLastIndexBy(c.arr, q.v, q.how & 2 ? 'x' : byFn)
                         : _.sortedIndexBy(c.arr, q.v, q.how & 2 ? 'x' : byFn);
    }
    if (q.how === 0) { return _.sortedIndexBy(c.arr, q.v, byFn); }
    if (q.how === 1) { return _.sortedLastIndexBy(c.arr, q.v, byFn); }
    if (typeof q.v !== 'number' || q.v !== q.v) { return q.how === 2 ? _.sortedIndex(c.arr, q.v) : _.sortedLastIndex(c.arr, q.v); }
    return q.how === 2 ? _.sortedIndexBy(c.arr, q.v, _.identity) : _.sortedLastIndexBy(c.arr, q.v, _.identity);
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(build);

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var res = [];
        for (var k = 0; k < cases[i].queries.length; k++) {
            try { res.push(run(cases[i], cases[i].queries[k])); } catch (e) { res.push('ERR:' + e.name); }
        }
        h.update(res.join(',') + '\n');
    }
    // huge sparse arrays and nullish arrays (iteratee call counts included)
    var extra = [];
    [Math.pow(2, 31), Math.pow(2, 32) - 1].forEach(function (len) {
        var a = []; a.length = len;
        [Math.pow(2, 32) - 1, NaN, undefined].forEach(function (v) {
            [_.sortedIndexBy, _.sortedLastIndexBy].forEach(function (f) {
                var steps = 0;
                extra.push(f(a, v, function (x) { steps++; return x; }), steps);
            });
        });
    });
    [null, undefined].forEach(function (a) { extra.push(_.sortedIndexBy(a, 1, byFn), _.sortedLastIndexBy(a, NaN, byFn)); });
    h.update(JSON.stringify(extra));
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) {
            var c = cases[j], qs = c.queries;
            for (var m = 0; m < qs.length; m++) { acc += run(c, qs[m]); }
        }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
