# Change these variables as necessary.
MAIN_PACKAGE_PATH := ./cmd/go_vanilla
BINARY_NAME := go_vanilla

## tidy: format code and tidy modfile
.PHONY: tidy
tidy:
	go fmt ./...
	go mod tidy -v

## build: build the application
.PHONY: build
build:
	# Include additional build steps, like TypeScript, SCSS or Tailwind compilation here...
	# go build -o=/tmp/bin/${BINARY_NAME} ${MAIN_PACKAGE_PATH}
	go build -o=./build/${BINARY_NAME} ${MAIN_PACKAGE_PATH}

## run: run the  application
.PHONY: run
run: build
	# /tmp/bin/${BINARY_NAME}
	./build/${BINARY_NAME}