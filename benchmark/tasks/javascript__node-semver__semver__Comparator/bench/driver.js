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
// Bench driver for the Comparator constructor: `new Comparator(input, options)` once per case.
// Existing-Comparator inputs (S only) are built outside the timed region.
var Comparator = semver.Comparator, SemVer = semver.SemVer;
var cases = raw.map(function (c) {
  var input = 'cc' in c ? new Comparator(c.cc[0], opt(c.cc[1])) : c.c;
  return { input: input, o: opt(c.o) };
});
run(cases, function (c) { return new Comparator(c.input, c.o); },
  function (out, c) {
    var sv = out.semver instanceof SemVer ? out.semver.version + '/' + out.semver.raw + '/' + out.semver.loose : 'ANY:' + JSON.stringify(out.semver);
    return [out === c.input, out instanceof Comparator, out.value, out.operator, out.loose,
      JSON.stringify(out.options), sv, String(out)].join('|');
  });
