/*
 * Minimal replacement for moment's `grunt transpile-raw` (tasks/transpile.js), limited to
 * what the node unit tests need: build/umd/moment.js and build/umd/test/moment/*.js.
 * Same rollup UMD output + header templates + skipLines as the original task.
 * usage (cwd = repo root, rollup in ./node_modules): node /opt/tc/moment-build.js
 */
'use strict';
var path = require('path');
var fs = require('fs');
var rollup = require(path.resolve('node_modules/rollup')).rollup;

function mkdirp(d) { if (!fs.existsSync(d)) { mkdirp(path.dirname(d)); fs.mkdirSync(d); } }

function build(entry, target, header, skipLines, skipMoment, umdName) {
    var ropts = { input: entry }, bopts = { format: 'umd', name: umdName || 'not_used' };
    if (skipMoment) {
        ropts.external = ['./moment', '../moment', '../../moment', path.resolve('src/moment')];
        bopts.globals = {};
        bopts.globals[path.resolve('src/moment')] = 'moment';
    }
    return rollup(ropts).then(function (b) { return b.generate(bopts); }).then(function (r) {
        var hdr = header === 'none' ? '' : fs.readFileSync(header, 'utf8');
        mkdirp(path.dirname(target));
        fs.writeFileSync(target, hdr + r.code.split('\n').slice(skipLines).join('\n'));
    });
}

var tests = fs.readdirSync('src/test/moment').filter(function (f) { return /\.js$/.test(f); });
build('src/moment.js', 'build/umd/moment.js', 'templates/default.js', 5, false, 'moment')
    .then(function () {
        return Promise.all(tests.map(function (f) {
            return build('src/test/moment/' + f, 'build/umd/test/moment/' + f,
                'templates/test-header.js', 7, true);
        }));
    })
    .then(function () { console.log('built moment + ' + tests.length + ' test modules'); },
          function (e) { console.error('build failed:', e && e.message); process.exit(1); });
