'use strict';
// Bench driver for lodash truncate (public `_.truncate`). argv: <size> <repeat> <mode: check|time>
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');

var WORDS = ['hi', 'diddly', 'ho', 'there', 'neighborino', 'a', 'lorem', 'ipsum', 'dolor', 'sit', 'amet',
    'consectetur', 'x', 'tempor', 'incididunt', 'labore', 'magna', 'aliqua', 'zzz', 'quux'];
var UWORDS = ['🍂', 'café', 'café', '🚀🚀', 'näive', '❤️',
    '👨‍👩‍👧', '🇺🇸', 'résumé'];

function lcg(seed) {
    var s = seed >>> 0;
    return function () { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s; };
}

function text(c) {
    var rnd = lcg(c.seed), parts = [];
    for (var i = 0; i < c.n; i++) {
        var r = rnd();
        var w = (c.uni && r % 5 === 0) ? UWORDS[(r >>> 8) % UWORDS.length] : WORDS[(r >>> 8) % WORDS.length];
        parts.push(w);
        parts.push((r >>> 20) % 7 === 0 ? ', ' : ((r >>> 20) % 11 === 1 ? '-' : ' '));
    }
    return parts.join('');
}

function opts(c) {
    var o = {};
    if (c.len !== null) { o.length = c.len; }
    if (c.om === '$null') { o.omission = null; } else if (c.om === '$undef') { o.omission = undefined; } else if (c.om !== null) { o.omission = c.om; }
    if (c.sep) { o.separator = c.sep.re ? new RegExp(c.sep.re[0], c.sep.re[1]) : c.sep.s; }
    return o;
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(function (c) {
    var noOpts = c.len === null && c.om === null && !c.sep;
    return { s: c.lit !== undefined ? c.lit : text(c), o: noOpts ? undefined : opts(c) };
});
var truncate = _.truncate;

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var out;
        try { out = JSON.stringify(truncate(cases[i].s, cases[i].o)); } catch (e) { out = 'ERR:' + e.name; }
        h.update(out + '\n');
    }
    var extra = [truncate(null), truncate(undefined), truncate(Object('hi-diddly-ho there'), { length: 4 }),
        truncate({ toString: function () { return 'hi-diddly-ho there'; } }, { length: 5 }),
        truncate('hi-diddly-ho there, neighborino', { length: { valueOf: function () { return 4.6; } } }),
        truncate('hi-diddly-ho there, neighborino', { length: { valueOf: function () { return '4'; } } }),
        truncate('hi-diddly-ho there, neighborino', { length: { valueOf: function () { return NaN; } } })]
        .concat(_.map(['hi-diddly-ho there, neighborino', 'short'], truncate));
    h.update(JSON.stringify(extra));
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) { acc += truncate(cases[j].s, cases[j].o).length; }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
