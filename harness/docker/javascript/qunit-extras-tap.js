/*
 * Preload for test suites that use `qunit-extras` (lodash):
 *   node -r /opt/tc/qunit-extras-tap.js test/test.js
 * Loads qunit-extras from the workspace, exposes it as global QUnit (the suite
 * picks up `root.QUnit`), and prints one TAP line per finished test so the
 * harness can parse per-test results (result_format "tap").
 */
'use strict';
var path = require('path');
var QUnit = require(path.resolve('node_modules/qunit-extras'));
global.QUnit = QUnit;
var n = 0;
function clean(s) { return String(s).replace(/[\r\n]+/g, ' ').replace(/#/g, 'No.'); }
QUnit.testDone(function (d) {
  n += 1;
  var status = d.failed ? 'not ok' : 'ok';
  process.stdout.write(status + ' ' + n + ' - ' + clean(d.module) + ' :: ' + clean(d.name) + '\n');
});
