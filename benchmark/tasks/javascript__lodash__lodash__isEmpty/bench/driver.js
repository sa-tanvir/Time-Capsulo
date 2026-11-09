'use strict';
// Bench driver for lodash isEmpty (public `_.isEmpty`). argv: <size> <repeat> <mode: check|time>
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');

var PRIMS = [null, undefined, false, true, 0, 1, NaN, '', Symbol('a'), /x/];
function makeArgs() { return arguments; }
function seq(n) { var a = new Array(n); for (var i = 0; i < n; i++) { a[i] = i; } return a; }
function keyed(target, n, prefix) { for (var i = 0; i < n; i++) { target[prefix + i] = i; } return target; }

function build(c) {
    var n = c.n;
    switch (c.kind) {
        case 'prim': return PRIMS[n];
        case 'arr': return seq(n);
        case 'str': return new Array(n + 1).join('x');
        case 'args': return makeArgs.apply(null, seq(n));
        case 'typed': return new Int16Array(n);
        case 'buffer': return Buffer.alloc(n);
        case 'splice': {
            var Q = function (els) { Array.prototype.push.apply(this, els); };
            Q.prototype = { length: 0, splice: Array.prototype.splice };
            return new Q(seq(n));
        }
        case 'map': { var m = new Map(); for (var i = 0; i < n; i++) { m.set('k' + i, i); } return m; }
        case 'set': { var s = new Set(); for (var j = 0; j < n; j++) { s.add(j); } return s; }
        case 'obj': return keyed({}, n, 'k');
        case 'inherit': {
            // chain of 4 prototypes sharing n enumerable keys, instance with `own` own keys
            var p = {}, per = Math.ceil(n / 4);
            for (var d = 0; d < 4; d++) { p = keyed(Object.create(p), Math.min(per, n - d * per), 'p' + d + '_'); }
            return keyed(Object.create(p), c.own, 'o');
        }
        case 'proto': {
            var F = function () {};
            F.prototype = keyed({ constructor: F }, n, 'm');
            if (!c.own) { /* keep */ } else { Object.defineProperty(F.prototype, 'extra', { value: 1, enumerable: true }); }
            return F.prototype;
        }
        case 'lenobj': {
            if (c.own) { var G = function () {}; G.prototype.length = n; return new G(); }
            return { length: n };
        }
        case 'func': return keyed(function () {}, n, 'f');
    }
    throw new Error('bad kind ' + c.kind);
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var values = raw.map(build);
var isEmpty = _.isEmpty;

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < values.length; i++) {
        var o;
        try { o = String(isEmpty(values[i])) + ':' + typeof isEmpty(values[i]); } catch (e) { o = 'ERR:' + e.name; }
        h.update(o + '\n');
    }
    h.update('noarg:' + isEmpty() + '|chain:' + _({}).isEmpty());
    console.log(JSON.stringify({ cases: values.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < values.length; j++) { if (isEmpty(values[j])) { acc++; } }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: values.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
