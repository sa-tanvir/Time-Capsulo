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
// Bench driver for Range.prototype.test: Range objects (and SemVer arguments marked {"$sv"}) are built
// outside the timed region; each (range, version) pair is one call. Invalid ranges are skipped.
var Range = semver.Range, SemVer = semver.SemVer;
var cases = [];
raw.forEach(function (c) {
  var r;
  try { r = new Range(c.r, opt(c.o)); } catch (e) { return; }
  c.vs.forEach(function (v) {
    if (v !== null && typeof v === 'object') {
      try { v = new SemVer(v.$sv, opt(c.o)); } catch (e) { return; }
    }
    cases.push({ r: r, v: v === null ? undefined : v });
  });
});
run(cases, function (c) { return c.r.test(c.v); }, function (out) { return String(out); });
