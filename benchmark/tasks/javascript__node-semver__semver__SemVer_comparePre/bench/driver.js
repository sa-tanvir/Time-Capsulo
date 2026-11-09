'use strict';
var fs = require('fs');
var crypto = require('crypto');
var semver = require('/w/semver.js');
var size = process.argv[2];
var repeat = parseInt(process.argv[3], 10);
var mode = process.argv[4];
var raw = JSON.parse(fs.readFileSync('/task/bench/workload_' + size + '.json', 'utf8'));
function opt(o) { return o === null ? undefined : o; }
// run(cases, call, canon, fresh): fresh(c) rebuilds mutable inputs outside the timed region
function run(cases, call, canon, fresh) {
  var i, o;
  if (mode === 'check') {
    var h = crypto.createHash('sha256');
    for (i = 0; i < cases.length; i++) {
      var inp = fresh ? fresh(cases[i]) : cases[i];
      try {
        o = canon(call(inp), inp);
      } catch (e) {
        o = 'ERR:' + e.name + ':' + e.message;
      }
      h.update(o + '\n');
    }
    console.log(JSON.stringify({ cases: cases.length, output_digest: h.digest('hex') }));
    return;
  }
  var acc = 0, elapsed = 0;
  for (var r = 0; r < repeat; r++) {
    var inputs = fresh ? cases.map(fresh) : cases;
    var t0 = process.hrtime();
    for (i = 0; i < inputs.length; i++) {
      try {
        o = call(inputs[i]);
        acc += o ? 1 : 2;
      } catch (e) {
        acc += 3;
      }
    }
    var dt = process.hrtime(t0);
    elapsed += dt[0] + dt[1] / 1e9;
  }
  process.stderr.write('checksum ' + acc + '\n');
  console.log(JSON.stringify({ cases: cases.length, repeat: repeat, elapsed_s: elapsed }));
}
// ---- task-specific part ----
// Bench driver for SemVer.prototype.comparePre (receiver and argument are built outside the timed region).
var SemVer = semver.SemVer;
function mk(p) {
  var s = new SemVer(p[0]);
  if (p[1] !== null) { s.prerelease = p[1]; }
  return s;
}
var cases = raw.map(function (c) { return { a: mk(c.a), b: 'bs' in c ? c.bs : mk(c.b) }; });
run(cases, function (c) { return c.a.comparePre(c.b); }, function (out) { return String(out); });
