# syntax=docker/dockerfile:1

# Debian-based image: ships gcc/libc, which `go test -race` needs (cgo).
# Alpine would require `apk add build-base` on top.
FROM golang:1.26-bookworm

ENV CGO_ENABLED=1 \
    GOTOOLCHAIN=local \
    GOCACHE=/tmp/go-cache \
    GOPATH=/tmp/go

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin tester
USER tester

WORKDIR /src

# Module files first so this layer is cached when only sources change.
# There are no dependencies (no go.sum); copy go.sum here once some appear.
COPY go.mod ./

COPY *.go ./

# Compile-check the package and tests with the race detector at build time
# (go build is not usable: package main has no main function).
RUN go vet ./... && go test -race -c -o /dev/null ./...

# Tests run at container start (not in a RUN layer) so results are never cached.
CMD ["go", "test", "-v", "-race", "-count=1", "./..."]
