'use strict';
// Bench driver for utils.arrayToObject. argv: <size> <repeat> <mode: check|time>
var fs = require('fs');
var crypto = require('crypto');
var utils = require('/w/lib/utils.js');
var arrayToObject = utils.arrayToObject;

function decodeElem(v) {
    if (v !== null && typeof v === 'object' && !Array.isArray(v) && '$undef' in v) { return undefined; }
    return v;
}

function build(c) {
    var base = c.base.map(decodeElem);
    var arr = new Array(c.len);
    for (var i = 0; i < c.len; i++) {
        if (c.holes > 0 && i % c.holes === 0) { continue; }
        arr[i] = (c.undef > 0 && i % c.undef === c.undef - 1) ? undefined : base[i % base.length];
    }
    return arr;
}

function canon(o) {
    var keys = Object.keys(o);
    var parts = [Array.isArray(o) ? 'A' : 'O', Object.getPrototypeOf(o) === null ? 'null' : 'obj', keys.length];
    for (var i = 0; i < keys.length; i++) {
        var v = o[keys[i]];
        parts.push(keys[i] + ':' + (v === undefined ? 'U' : JSON.stringify(v)));
    }
    return parts.join('|');
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(function (c) {
    return { src: build(c), opts: c.opts === null ? undefined : c.opts };
});

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var o;
        try {
            o = canon(arrayToObject(cases[i].src, cases[i].opts));
        } catch (e) {
            o = 'ERR:' + e.name;
        }
        h.update(o + '\n');
    }
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) {
            var res = arrayToObject(cases[j].src, cases[j].opts);
            acc += res[1] === undefined ? 1 : 2;
        }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
