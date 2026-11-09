/*
 * Run QUnit (npm `qunit` 2.x) test files under plain node, exposing QUnit as a global
 * (moment's tests use the global), and print one TAP line per finished test.
 * usage: node /opt/tc/qunit-tap.js file1.js [file2.js ...]   (cwd = repo root)
 */
'use strict';
var path = require('path');
var QUnit = require(path.resolve('node_modules/qunit'));
global.QUnit = QUnit;
QUnit.config.autostart = false;
var n = 0;
function clean(s) { return String(s).replace(/[\r\n]+/g, ' ').replace(/#/g, 'No.'); }
QUnit.testDone(function (d) {
    n += 1;
    process.stdout.write((d.failed ? 'not ok' : 'ok') + ' ' + n + ' - ' + clean(d.module) + ' :: ' + clean(d.name) + '\n');
});
QUnit.done(function (d) { process.stdout.write('1..' + n + '\n# passed ' + d.passed + ' failed ' + d.failed + '\n'); });
process.argv.slice(2).forEach(function (f) {
    try { require(path.resolve(f)); }
    catch (e) { process.stdout.write('# load error ' + f + ': ' + (e && e.message) + '\n'); }
});
QUnit.start();
