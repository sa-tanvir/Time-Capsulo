/*
 * Runner for tape suites (qs):  node /opt/tc/tape-tap.js test/index.js [...]
 * Prints one TAP line per tape test (not per assertion) so that per-test results
 * are stable when an assertion count changes. A synchronous exception thrown by a
 * test body fails that test instead of aborting the whole process.
 */
'use strict';
var path = require('path');
var tape = require(path.resolve('node_modules/tape'));
var Test = require(path.resolve('node_modules/tape/lib/test'));

var origRun = Test.prototype.run;
Test.prototype.run = function () {
  try {
    return origRun.apply(this, arguments);
  } catch (e) {
    this.error(e, 'uncaught exception in test body');
    if (!this.ended) { this.end(); }
    this.emit('run');
  }
};

var tests = {}, n = 0, current = null;
function clean(s) { return String(s).replace(/[\r\n]+/g, ' ').replace(/#/g, 'No.'); }
function fullName(id) {
  var t = tests[id], parts = [];
  while (t) { parts.unshift(t.name); t = tests[t.parent]; }
  return parts.join(' > ');
}
var stream = tape.createStream({ objectMode: true });
stream.on('data', function (row) {
  if (row.type === 'test') {
    tests[row.id] = { name: clean(row.name), parent: row.parent, failed: false };
    current = row.id;
  } else if (row.type === 'assert') {
    if (!row.ok && !row.todo && !row.skip && tests[row.test]) {
      var id = row.test;
      while (id !== undefined && tests[id]) { tests[id].failed = true; id = tests[id].parent; }
    }
  } else if (row.type === 'end') {
    var t = tests[row.test];
    if (!t) { return; }
    n += 1;
    process.stdout.write((t.failed ? 'not ok ' : 'ok ') + n + ' - ' + fullName(row.test) + '\n');
  }
});
process.on('uncaughtException', function (e) {
  if (current !== null && tests[current]) {
    n += 1;
    process.stdout.write('not ok ' + n + ' - ' + fullName(current) + '\n');
  }
  process.stderr.write('uncaught exception: ' + (e && e.stack || e) + '\n');
  process.exit(1);
});
process.argv.slice(2).forEach(function (f) { require(path.resolve(f)); });
