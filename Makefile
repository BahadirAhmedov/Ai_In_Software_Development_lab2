test:
	go test -v -race

docker-build:
	docker build -t hw-signer .

docker-test:
	docker run --rm hw-signer

.PHONY: test docker-build docker-test
