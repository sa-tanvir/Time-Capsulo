# Era toolchain for Go repos (2017-2019): Go 1.13 (Sep 2019) on Alpine.
# Build: docker build -t tc-go -f harness/docker/go.Dockerfile harness/docker
# Base image pinned by digest (checked on 2026-10-20 to be the exact base of the images used for all published results).
FROM golang:1.13-alpine@sha256:e74b83b94d499cb34c7edf55fbdff9d3cfabd238a35f9cb1b59d0e74f50b1ddd
RUN apk add --no-cache bash git
ENV CGO_ENABLED=0 GO111MODULE=on GOPROXY=off GOSUMDB=off \
    GOCACHE=/root/.cache/go-build
COPY go-test-each.sh /usr/local/bin/go-test-each
RUN chmod +x /usr/local/bin/go-test-each
WORKDIR /w
# goimports (x/tools release-branch.go1.13, commit 991d59a): applied to every injected Go file (reference and model code alike) so that an import used only by
# the replaced function, or missing from a model's answer, does not turn into a compile error. Pinned version.
RUN GOPROXY=https://proxy.golang.org GOFLAGS= go get golang.org/x/tools/cmd/goimports@991d59a616deaaf84d86e0819e386431a7a31b87 \
    && mv /go/bin/goimports /usr/local/bin/goimports && rm -rf /go/pkg/mod/* /root/.cache/go-build/*
