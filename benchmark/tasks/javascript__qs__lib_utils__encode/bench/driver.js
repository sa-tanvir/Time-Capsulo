'use strict';
// Bench driver for utils.encode. argv: <size> <repeat> <mode: check|time>
var fs = require('fs');
var crypto = require('crypto');
var utils = require('/w/lib/utils.js');
var encode = utils.encode;

function build(v, rep) {
    if (typeof v === 'string') { return v.repeat(rep); }
    if (v !== null && typeof v === 'object') {
        if ('$buf' in v) { return Buffer.from(v.$buf, 'utf8'); }
        if ('$sym' in v) { return Symbol(v.$sym); }
    }
    return v;
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(function (c) {
    return { s: build(c.v, c.rep), charset: c.charset === null ? undefined : c.charset };
});

function canon(out) {
    if (typeof out === 'string') { return JSON.stringify(out); }
    if (Buffer.isBuffer(out)) { return 'BUF:' + out.toString('hex'); }
    return typeof out + ':' + JSON.stringify(out);
}

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var o;
        try {
            o = canon(encode(cases[i].s, encode, cases[i].charset));
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
            acc += encode(cases[j].s, encode, cases[j].charset).length;
        }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
