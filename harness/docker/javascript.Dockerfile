# Era toolchain for JavaScript repos (2017-2019): Node.js 10 LTS + npm 6
# Build: docker build -f harness/docker/javascript.Dockerfile -t tc-javascript harness/docker
# Base image pinned by digest (checked on 2026-10-20 to be the exact base of the images used for all published results).
FROM node:10-slim@sha256:88932859e3d022d79161b99628c4c2c50e836437455e2d1b1a008d98367b10d6
ENV NPM_CONFIG_UPDATE_NOTIFIER=false NPM_CONFIG_FUND=false NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_PROGRESS=false NPM_CONFIG_LOGLEVEL=warn TZ=UTC
# Small test-runner adapters that print one TAP line per test (see javascript/README)
COPY javascript/ /opt/tc/
WORKDIR /w
