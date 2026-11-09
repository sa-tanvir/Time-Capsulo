'use strict';
// Bench driver for lodash arrayLikeKeys. argv: <size> <repeat> <mode: check|time>
// arrayLikeKeys is internal; it is reached through the public _.keys(v) / _.keysIn(v), which for
// array-like values do nothing but call arrayLikeKeys(v) / arrayLikeKeys(v, true).
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');

function makeArgs() { return arguments; }

function build(c) {
    var v, i, n = c.n;
    if (c.kind === 'arr' || c.kind === 'args') {
        var a = new Array(n);
        for (i = 0; i < n; i++) { a[i] = i; }
        v = c.kind === 'arr' ? a : makeArgs.apply(null, a);
        if (c.holes > 0) { for (i = 0; i < n; i += c.holes) { delete v[i]; } }
    } else if (c.kind === 'typed') {
        v = n % 2 ? new Float64Array(n) : new Uint8Array(n);
    } else if (c.kind === 'buffer') {
        v = Buffer.alloc(n);
    } else if (c.kind === 'strobj' || c.kind === 'str') {
        var s = '';
        for (i = 0; i < n; i++) { s += String.fromCharCode(97 + (i % 26)); }
        v = c.kind === 'str' ? s : Object(s);
    } else {
        v = { length: n };
        for (i = 0; i < n; i++) { v[i] = i; }
    }
    if (c.proto.length && typeof v === 'object') {
        var p = Object.create(Object.getPrototypeOf(v));
        c.proto.forEach(function (k) { Object.defineProperty(p, k, { value: 1, enumerable: true, writable: true, configurable: true }); });
        Object.setPrototypeOf(v, p);
    }
    if (typeof v === 'object') {
        c.extra.forEach(function (k) {
            try { Object.defineProperty(v, k, { value: 1, enumerable: true, writable: true, configurable: true }); } catch (e) { /* non-configurable (e.g. array length) */ }
        });
    }
    return v;
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(function (c) { return { v: build(c), fn: c.inherited ? _.keysIn : _.keys }; });

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var o;
        try { o = JSON.stringify(cases[i].fn(cases[i].v)); } catch (e) { o = 'ERR:' + e.name; }
        h.update(o + '\n');
    }
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) { acc += cases[j].fn(cases[j].v).length; }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
