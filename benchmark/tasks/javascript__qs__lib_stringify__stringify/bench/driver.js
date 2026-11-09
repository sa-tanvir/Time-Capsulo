'use strict';
// Bench driver for qs stringify. argv: <size> <repeat> <mode: check|time>
var fs = require('fs');
var crypto = require('crypto');
var qs = require('/w/lib/index.js');

var FNS = {
    sortAsc: function (a, b) { return a < b ? -1 : a > b ? 1 : 0; },
    sortDesc: function (a, b) { return a < b ? 1 : a > b ? -1 : 0; },
    filterDatesToMs: function (prefix, value) { return value instanceof Date ? value.getTime() : value; },
    filterDropEveryThird: function (prefix, value) {
        if (prefix.length % 3 === 2) { return undefined; }
        return value instanceof Date ? value.toISOString() : value;
    },
    filterIdentity: function (prefix, value) { return value; },
    dateMs7: function (d) { return d.getTime() * 7; },
    dateNull: function () { return null; },
    encCase: function (str, defaultEncoder, charset, type) {
        var r = defaultEncoder(str, defaultEncoder, charset, type);
        return type === 'key' ? r.toLowerCase() : r.toUpperCase();
    },
    encWrap: function (str, defaultEncoder, charset, type) {
        return (type === 'key' ? 'K' : 'V') + defaultEncoder(str, defaultEncoder, charset) + '.';
    }
};

function decode(v) {
    if (Array.isArray(v)) { return v.map(decode); }
    if (v === null || typeof v !== 'object') { return v; }
    var keys = Object.keys(v);
    if (keys.length === 1 && keys[0].charAt(0) === '$') {
        var t = keys[0];
        var x = v[t];
        if (t === '$date') { return new Date(x); }
        if (t === '$buf') { return Buffer.from(x, 'utf8'); }
        if (t === '$undef') { return undefined; }
        if (t === '$sym') { return Symbol(x); }
        if (t === '$fn') { return FNS[x]; }
    }
    var out = {};
    for (var i = 0; i < keys.length; i++) { out[keys[i]] = decode(v[keys[i]]); }
    return out;
}

function run(c) {
    try {
        return c.opts === undefined ? qs.stringify(c.obj) : qs.stringify(c.obj, c.opts);
    } catch (e) {
        return 'ERR:' + e.name + ':' + e.message;
    }
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(function (c) {
    return { obj: decode(c.obj), opts: c.opts === null ? undefined : decode(c.opts) };
});

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        h.update(JSON.stringify(run(cases[i])) + '\n');
    }
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) {
            acc += run(cases[j]).length;
        }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
