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
// Bench driver for the Range constructor: `new Range(input, options)` once per case.
// Existing Range / Comparator inputs (S only) are built outside the timed region.
var Range = semver.Range, Comparator = semver.Comparator;
var cases = raw.map(function (c) {
  var input = c.r;
  if ('rr' in c) {
    try { input = new Range(c.rr[0], opt(c.rr[1])); } catch (e) { input = c.rr[0]; }
  } else if ('rc' in c) {
    input = new Comparator(c.rc, opt(c.o));
  }
  return { input: input, o: opt(c.o) };
});
run(cases, function (c) { return new Range(c.input, c.o); },
  function (out, c) {
    return [out === c.input, out instanceof Range, out.range, out.raw, out.loose, out.includePrerelease,
      JSON.stringify(out.options), JSON.stringify(out.set.map(function (s) {
        return s.map(function (x) { return [x.value, x.operator, x.loose]; });
      })), String(out)].join('|');
  });
