#!/bin/sh
# Install only the named devDependencies into /w/node_modules, ignoring the repo's
# package.json / lockfile (keeps the workspace small). Versions are resolved as of
# the given date (npm --before), so ranges pick 2019-era releases.
# usage: npm-install-isolated.sh <YYYY-MM-DD> pkg@range [pkg@range ...]
set -e
before="$1"; shift
rm -rf /tmp/tcnpm && mkdir -p /tmp/tcnpm && cd /tmp/tcnpm
echo '{"name":"tc-deps","version":"0.0.0","private":true}' > package.json
npm install --no-package-lock --no-save --before="$before" "$@"
rm -rf /w/node_modules
cp -a node_modules /w/node_modules
