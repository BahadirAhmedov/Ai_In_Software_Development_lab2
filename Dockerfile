FROM golang:1.26-bookworm

ENV CGO_ENABLED=1 \
    GOTOOLCHAIN=local \
    GOCACHE=/tmp/go-cache

WORKDIR /app

# Copy go.mod first to leverage layer caching when only source changes.
# go.sum is omitted intentionally — the project has no external dependencies.
COPY go.mod ./
RUN go mod download

COPY . .

# Compile-check at build time without producing a binary (no main function).
RUN go vet ./...

# Create a non-privileged user and ensure the Go cache dir is writable.
RUN useradd -r -s /bin/false appuser && \
    chown -R appuser:appuser /app /tmp/go-cache

USER appuser

CMD ["go", "test", "-v", "-race", "-count=1", "./..."]
