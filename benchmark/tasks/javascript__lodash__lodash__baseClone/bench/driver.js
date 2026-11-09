'use strict';
// Bench driver for lodash baseClone. argv: <size> <repeat> <mode: check|time>
// baseClone is internal; the public _.clone / _.cloneDeep / _.cloneWith / _.cloneDeepWith (from
// require('/w/lodash.js')) call it directly with the corresponding flags, so it does all the work.
var fs = require('fs');
var crypto = require('crypto');
var _ = require('/w/lodash.js');

function lcg(seed) {
    var s = seed >>> 0;
    return function () { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
}
function Point(x, y) { this.x = x; this.y = y; }
Point.prototype.norm = function () { return this.x + this.y; };
var SYM = Symbol('tag'), SYM2 = Symbol('hidden');
function sharedFn() { return 1; }
sharedFn.extra = 5;
var sharedErr = new TypeError('boom');

function leaf(rnd, i) {
    var r = rnd();
    if (r < 0.25) { return Math.floor(r * 1000); }
    if (r < 0.4) { return 's' + i; }
    if (r < 0.45) { return null; }
    if (r < 0.5) { return undefined; }
    if (r < 0.55) { return new Date(1500000000000 + i * 1000); }
    if (r < 0.6) { var re = /a(b+)c/gi; re.lastIndex = i % 5; return re; }
    if (r < 0.63) { var bx = Object(i % 2 ? 'str' : i); bx.note = i; return bx; }
    if (r < 0.66) { return new Point(i, -i); }
    if (r < 0.68) { var ta = new Float32Array(4); ta[0] = i; return ta; }
    if (r < 0.69) { return sharedFn; }
    if (r < 0.70) { return sharedErr; }
    if (r < 0.72) { return Object(Symbol.iterator); }
    return i % 3 === 0;
}

function container(rnd, i) {
    var r = rnd();
    if (r < 0.45) { var o = {}; if (i % 7 === 0) { o[SYM] = { s: i }; Object.defineProperty(o, SYM2, { value: 1, enumerable: false }); } return o; }
    if (r < 0.75) { var a = []; if (i % 5 === 0) { a.expando = i; } return a; }
    if (r < 0.85) { return new Map(); }
    if (r < 0.92) { return new Set(); }
    return new Point(i, i);
}

function put(c, k, v) {
    if (c instanceof Map) { c.set('m' + k, v); }
    else if (c instanceof Set) { c.add(v); }
    else if (Array.isArray(c)) { c.push(v); }
    else { c['k' + k] = v; }
}

function build(cs) {
    var rnd = lcg(cs.seed), n = cs.n, nodes = [], root, i;
    root = cs.shape === 'list' ? [] : {};
    nodes.push(root);
    var fan = cs.shape === 'wide' ? n : cs.shape === 'list' ? 1 : 6;
    for (i = 1; i < n; i++) {
        var parent = cs.shape === 'wide' ? root : cs.shape === 'list' ? nodes[nodes.length < 300 ? nodes.length - 1 : Math.floor(rnd() * nodes.length)] : nodes[Math.floor((i - 1) / fan)];
        if (!parent) { parent = root; }
        var isCont = cs.shape === 'list' ? (i % 4 !== 0) : rnd() < 0.3;   // list: a 300-level chain, then random attachment
        var v = isCont ? container(rnd, i) : leaf(rnd, i);
        if (cs.shape === 'graph' && rnd() < 0.15 && nodes.length > 1) { v = nodes[Math.floor(rnd() * Math.min(nodes.length, 20))]; isCont = false; }  // links only to near-root nodes keep recursion depth bounded
        put(parent, i, v);
        if (isCont) { nodes.push(v); }
    }
    if (cs.shape === 'graph') { root.self = root; }
    var cust;
    if (cs.fn === 'cloneDeepWith' || cs.fn === 'cloneWith') {
        cust = function (value) { return value instanceof Date ? 'D' + value.getTime() : (value instanceof Point && value.x % 2 ? 'P' : undefined); };
    }
    return { v: root, fn: _[cs.fn], cust: cust, deep: /Deep/.test(cs.fn) };
}

// canonical serialisation of a clone, with object identities numbered by first visit
function canon(v, orig) {
    var ids = new Map(), out = [], origSet = new Set();
    (function collect(o) {
        if (!o || typeof o !== 'object' && typeof o !== 'function' || origSet.has(o)) { return; }
        origSet.add(o);
        if (o instanceof Map || o instanceof Set) { o.forEach(function (x, k) { collect(x); }); }
        Object.keys(o).forEach(function (k) { collect(o[k]); });
    }(orig));
    (function walk(x, depth) {
        if (x === null || (typeof x !== 'object' && typeof x !== 'function')) {
            out.push(typeof x === 'symbol' ? 'Y' + String(x) : typeof x + ':' + String(x)); return;
        }
        if (ids.has(x)) { out.push('@' + ids.get(x)); return; }
        ids.set(x, ids.size);
        var tag = Object.prototype.toString.call(x), proto = Object.getPrototypeOf(x);
        out.push('{' + tag + (proto && proto.constructor ? proto.constructor.name : 'null') + (origSet.has(x) ? '=orig' : ''));
        if (typeof x === 'function') { out.push('fn'); }
        else if (x instanceof Date) { out.push(x.getTime()); }
        else if (x instanceof RegExp) { out.push(String(x) + x.lastIndex); }
        else if (ArrayBuffer.isView(x)) { out.push(Array.prototype.join.call(x, ',') + '|' + x.byteOffset); }
        else if (x instanceof Error) { out.push(x.message); }
        else if (typeof x.valueOf === 'function' && /Number|String|Boolean|Symbol/.test(tag)) { out.push(String(x.valueOf())); }
        if (x instanceof Map) { x.forEach(function (val, k) { out.push('k' + k); walk(val, depth + 1); }); }
        if (x instanceof Set) { x.forEach(function (val) { walk(val, depth + 1); }); }
        var keys = Object.keys(x);
        if (Array.isArray(x)) { out.push('len' + x.length); }
        for (var i = 0; i < keys.length; i++) { out.push(keys[i]); walk(x[keys[i]], depth + 1); }
        var syms = Object.getOwnPropertySymbols(x);
        for (var j = 0; j < syms.length; j++) { out.push(String(syms[j]) + Object.prototype.propertyIsEnumerable.call(x, syms[j])); walk(x[syms[j]], depth + 1); }
        out.push('}');
    }(v, 0));
    return out.join(' ');
}

var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
var cases = raw.map(build);

if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (var i = 0; i < cases.length; i++) {
        var o, c = cases[i];
        try { o = canon(c.cust ? c.fn(c.v, c.cust) : c.fn(c.v), c.v); } catch (e) { o = 'ERR:' + e.name; }
        h.update(crypto.createHash('sha256').update(o).digest('hex') + '\n');
    }
    var log = [];
    _.cloneDeepWith(new Point(1, 2), function () { log.push(arguments.length + ':' + typeof arguments[0]); });
    h.update(log.join(',') + '|' + canon(_.clone(sharedFn), {}) + '|' + canon(_.cloneDeep(sharedErr), {}) + '|' + canon(_.clone(/c/.exec('abcde')), {}));
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
} else {
    var acc = 0;
    var t0 = process.hrtime();
    for (var r = 0; r < repeat; r++) {
        for (var j = 0; j < cases.length; j++) {
            var cc = cases[j], res = cc.cust ? cc.fn(cc.v, cc.cust) : cc.fn(cc.v);
            acc += res === cc.v ? 1 : 2;
        }
    }
    var dt = process.hrtime(t0);
    process.stderr.write('checksum ' + acc + '\n');
    console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: dt[0] + dt[1] / 1e9 }));
}
